#!/usr/bin/env python3
"""Demo script for dashboard ingestion workflow.
Generates synthetic data and shows complete pipeline:
export -> validate -> ingest -> query

Usage (requires InfluxDB running):
  PYTHONPATH=. python3 dashboard/scripts/demo_ingestion.py

Prerequisites:
- InfluxDB running on localhost:8086  
- .env configured with INFLUXDB_TOKEN
- pip install influxdb-client
"""
from __future__ import annotations
import subprocess, sys, pathlib
import tempfile, os

def run_command(cmd: list[str], description: str) -> bool:
    """Run command and return success status."""
    print(f"🔄 {description}")
    print(f"   Command: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True, env=os.environ.copy())
        if result.stdout:
            for line in result.stdout.strip().split('\n'):
                print(f"   {line}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed: {e}")
        if e.stdout:
            print(f"   stdout: {e.stdout}")
        if e.stderr:
            print(f"   stderr: {e.stderr}")
        return False

def main():
    print("🚀 Dashboard Ingestion Pipeline Demo")
    print("="*50)
    
    # Check prerequisites
    env_path = pathlib.Path(".env")
    if not env_path.exists():
        print("❌ Missing .env file. Copy .env.example and configure INFLUXDB_TOKEN")
        return 1
    
    # Use temp file for demo
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as tmp:
        tmp_path = pathlib.Path(tmp.name)
    
    try:
        # Step 1: Generate synthetic historical data
        if not run_command([
            "python3", "dashboard/scripts/export_historical.py", str(tmp_path)
        ], "Step 1: Generate synthetic 30-day historical data"):
            return 1
        
        # Step 2: Validate the exported data
        if not run_command([
            "python3", "dashboard/scripts/validate_daily_records.py", str(tmp_path)
        ], "Step 2: Validate exported records"):
            return 1
        
        # Step 3: Ingest into InfluxDB
        if not run_command([
            "python3", "dashboard/scripts/ingest_influxdb.py", str(tmp_path)
        ], "Step 3: Ingest into InfluxDB"):
            return 1
        
        print("\n✅ Complete pipeline demo successful!")
        print(f"📊 Data ingested into InfluxDB measurements:")
        print(f"   - wb_score: daily scores with band tags")
        print(f"   - wb_contrib: per-metric contributions") 
        print(f"   - wb_quality: completeness and error tracking")
        print(f"\n🎯 Ready for Grafana panel creation!")
        
        return 0
        
    finally:
        # Clean up temp file
        if tmp_path.exists():
            tmp_path.unlink()

if __name__ == "__main__":
    # Set PYTHONPATH to current directory
    current_dir = pathlib.Path.cwd()
    os.environ["PYTHONPATH"] = str(current_dir)
    
    raise SystemExit(main())