#!/usr/bin/env python3
"""InfluxDB ingestion script for well-being dashboard.
Reads JSON Lines daily records and writes to InfluxDB measurements.

Measurements created:
- wb_score: score, band, formula_version  
- wb_contrib: per-metric contributions
- wb_quality: completeness and error metrics

Usage:
  PYTHONPATH=. python3 dashboard/scripts/ingest_influxdb.py input.jsonl

Requires:
  pip install influxdb-client
  
Environment (.env):
  INFLUXDB_URL=http://localhost:8086
  INFLUXDB_ORG=local
  INFLUXDB_BUCKET=garmin
  INFLUXDB_TOKEN=your_token
"""
from __future__ import annotations
import os, sys, json, pathlib
from typing import Any, Dict
from datetime import datetime, timezone
import time

try:
    from influxdb_client import InfluxDBClient, Point, WritePrecision
    from influxdb_client.client.write_api import SYNCHRONOUS
except ImportError as e:
    print("Missing dependency: influxdb-client. Install with 'pip install influxdb-client'", file=sys.stderr)
    sys.exit(2)

# Load environment variables
def load_env():
    env_path = pathlib.Path(".env")
    env_vars = {}
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env_vars[key.strip()] = value.strip()
    return env_vars

def get_config():
    """Get InfluxDB configuration from environment."""
    env_vars = load_env()
    
    config = {
        "url": env_vars.get("INFLUXDB_URL") or os.getenv("INFLUXDB_URL", "http://localhost:8086"),
        "org": env_vars.get("INFLUXDB_ORG") or os.getenv("INFLUXDB_ORG", "local"), 
        "bucket": env_vars.get("INFLUXDB_BUCKET") or os.getenv("INFLUXDB_BUCKET", "garmin"),
        "token": env_vars.get("INFLUXDB_TOKEN") or os.getenv("INFLUXDB_TOKEN", "")
    }
    
    if not config["token"]:
        raise ValueError("INFLUXDB_TOKEN not found in .env or environment")
    
    return config

def parse_date(date_str: str) -> datetime:
    """Parse YYYY-MM-DD date to datetime."""
    return datetime.fromisoformat(date_str).replace(tzinfo=timezone.utc)

def create_wb_score_point(record: Dict[str, Any]) -> Point:
    """Create wb_score measurement point."""
    point = Point("wb_score") \
        .tag("band", record["band"]) \
        .tag("formula_version", record["formula_version"]) \
        .tag("run_mode", record.get("run_mode", "unknown")) \
        .field("score", record["score"]) \
        .time(parse_date(record["date"]), WritePrecision.D)
    return point

def create_wb_contrib_points(record: Dict[str, Any]) -> list[Point]:
    """Create wb_contrib measurement points (one per metric)."""
    points = []
    date = parse_date(record["date"])
    
    for metric, contrib_value in record["contrib"].items():
        point = Point("wb_contrib") \
            .tag("metric", metric) \
            .tag("formula_version", record["formula_version"]) \
            .field("contribution", float(contrib_value)) \
            .field("weight", float(record["weights_active"].get(metric, 0.0))) \
            .time(date, WritePrecision.D)
        points.append(point)
    
    return points

def create_wb_quality_point(record: Dict[str, Any]) -> Point:
    """Create wb_quality measurement point."""
    total_possible = len(record["metrics_raw"])
    missing_count = len(record.get("missing", []))
    present_count = total_possible - missing_count
    completeness_pct = (present_count / total_possible * 100) if total_possible > 0 else 100.0
    
    point = Point("wb_quality") \
        .tag("formula_version", record["formula_version"]) \
        .field("metrics_present", present_count) \
        .field("metrics_expected", total_possible) \
        .field("missing_count", missing_count) \
        .field("completeness_pct", completeness_pct) \
        .field("error_count", len(record.get("error_codes", []))) \
        .time(parse_date(record["date"]), WritePrecision.D)
    
    return point

def ingest_records(client: InfluxDBClient, config: dict, records_path: pathlib.Path) -> int:
    """Ingest all records from JSON Lines file."""
    write_api = client.write_api(write_options=SYNCHRONOUS)
    
    ingested_count = 0
    batch_points = []
    
    with open(records_path, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
                
            try:
                record = json.loads(line)
                
                # Create points for all measurements
                batch_points.append(create_wb_score_point(record))
                batch_points.extend(create_wb_contrib_points(record))
                batch_points.append(create_wb_quality_point(record))
                
                ingested_count += 1
                
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                print(f"Warning: Skipping line {line_no}: {e}", file=sys.stderr)
                continue
    
    if batch_points:
        write_api.write(bucket=config["bucket"], org=config["org"], record=batch_points)
        print(f"Ingested {ingested_count} records into InfluxDB ({len(batch_points)} total points)")
    else:
        print("No valid records found to ingest")
    
    return ingested_count

def main():
    if len(sys.argv) != 2:
        print("Usage: ingest_influxdb.py <records.jsonl>", file=sys.stderr)
        return 1
    
    records_path = pathlib.Path(sys.argv[1])
    if not records_path.exists():
        print(f"File not found: {records_path}", file=sys.stderr)
        return 1
    
    try:
        config = get_config()
        print(f"Connecting to InfluxDB: {config['url']} (bucket: {config['bucket']})")
        
        with InfluxDBClient(url=config["url"], token=config["token"], org=config["org"]) as client:
            # Test connection
            try:
                health = client.health()
                if health.status != "pass":
                    raise Exception(f"InfluxDB health check failed: {health.status}")
                print("✅ InfluxDB connection healthy")
            except Exception as e:
                print(f"❌ InfluxDB connection failed: {e}", file=sys.stderr)
                return 1
            
            # Ingest records
            count = ingest_records(client, config, records_path)
            print(f"✅ Successfully ingested {count} daily records")
            
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())