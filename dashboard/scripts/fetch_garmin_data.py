#!/usr/bin/env python3
"""
Fetch wellness data from Garmin Connect and convert to our schema.
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from garminconnect import Garmin

# Import Phase 3 modules and score engine
dashboard_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, dashboard_path)
from scripts.phase3.auto_run_tracker import add_auto_run_flag
from scripts.phase3.battery_safeguard import should_skip_battery
from score.engine import compute_score, MetricInputs, ScoreFlags, map_score_to_band
from utils.file_utils import atomic_append_jsonl

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GarminWellnessFetcher:
    """Fetch and transform Garmin Connect data to our wellness schema."""
    
    def __init__(self, email: str, password: str):
        """Initialize Garmin client."""
        self.email = email
        self.password = password
        self.client = None
        
    def connect(self) -> bool:
        """Establish connection to Garmin Connect."""
        try:
            logger.info("Connecting to Garmin Connect...")
            self.client = Garmin(self.email, self.password)
            self.client.login()
            logger.info("Successfully connected to Garmin Connect")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Garmin Connect: {e}")
            return False
    
    def fetch_daily_data(self, date: datetime) -> Optional[Dict]:
        """
        Fetch wellness data for a specific date.
        
        Returns data in our wellness schema format:
        {
            "date": "YYYY-MM-DD",
            "metrics": {
                "steps": int,
                "restingHeartRate": int,
                "sleepHours": float,
                "stress": int (0-100)
            },
            "score": int,
            "band": str
        }
        """
        if not self.client:
            logger.error("Not connected to Garmin")
            return None
            
        try:
            date_str = date.strftime("%Y-%m-%d")
            logger.info(f"Fetching data for {date_str}")
            
            # Fetch various metrics from Garmin
            # 1. Steps
            steps_data = self.client.get_steps_data(date_str)
            steps = steps_data[0]['steps'] if steps_data else 0
            
            # 2. Heart Rate (get resting HR from daily stats)
            hr_data = self.client.get_heart_rates(date_str)
            resting_hr = 60  # Default
            if hr_data and 'restingHeartRate' in hr_data:
                resting_hr = hr_data['restingHeartRate']
            
            # 3. Sleep (convert seconds to hours)
            sleep_data = self.client.get_sleep_data(date_str)
            sleep_hours = 0.0
            if sleep_data and 'dailySleepDTO' in sleep_data:
                sleep_seconds = sleep_data['dailySleepDTO'].get('sleepTimeSeconds', 0)
                sleep_hours = round(sleep_seconds / 3600, 1)
            
            # 4. Stress (average stress level)
            stress_data = self.client.get_stress_data(date_str)
            stress_level = 50  # Default medium stress
            if stress_data and isinstance(stress_data, list) and len(stress_data) > 0:
                # Calculate average stress from available readings
                stress_values = [s.get('stressLevel', 0) for s in stress_data 
                                if s.get('stressLevel') is not None and s.get('stressLevel') > 0]
                if stress_values:
                    stress_level = int(sum(stress_values) / len(stress_values))
            
            # Build our wellness record
            record = {
                "date": date_str,
                "metrics": {
                    "steps": steps,
                    "restingHeartRate": resting_hr,
                    "sleepHours": sleep_hours,
                    "stress": stress_level
                }
            }
            
            # Calculate wellness score using our formula
            score = self.calculate_wellness_score(record['metrics'])
            record['score'] = score
            record['band'] = self.get_band(score)
            
            # Phase 3: Add auto-run flag (AC1)
            record = add_auto_run_flag(record)
            
            logger.info(f"Fetched data for {date_str}: Score={score}, Steps={steps}, "
                       f"RHR={resting_hr}, Sleep={sleep_hours}h, Stress={stress_level}, "
                       f"AutoRun={record.get('auto_run', 0)}")
            
            return record
            
        except Exception as e:
            logger.error(f"Error fetching data for {date}: {e}")
            return None
    
    def calculate_wellness_score(self, metrics: Dict) -> int:
        """
        Calculate wellness score using the unified score engine.
        This ensures consistency with dashboard/score/engine.py
        """
        # Convert metrics to engine format
        inputs = MetricInputs(
            steps=metrics.get('steps'),
            rhr=metrics.get('restingHeartRate'),
            sleep_hours=metrics.get('sleepHours'),
            stress=metrics.get('stress')
        )
        
        # Use flags based on metric availability (Phase 3 approach)
        flags = ScoreFlags(
            enable_sleep=metrics.get('sleepHours') is not None,
            enable_stress=metrics.get('stress') is not None,
            enable_hrv=False  # Not implemented yet
        )
        
        result = compute_score(inputs, flags)
        return result.score
    
    def get_band(self, score: int) -> str:
        """Get wellness band based on score using centralized mapping."""
        return map_score_to_band(score)
    
    def fetch_date_range(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Fetch data for a date range."""
        records = []
        current_date = start_date
        
        while current_date <= end_date:
            record = self.fetch_daily_data(current_date)
            if record:
                records.append(record)
            current_date += timedelta(days=1)
            
        return records
    
    def fetch_last_n_days(self, days: int = 30) -> List[Dict]:
        """Fetch data for the last N days."""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days-1)
        
        return self.fetch_date_range(
            datetime.combine(start_date, datetime.min.time()),
            datetime.combine(end_date, datetime.min.time())
        )

def save_telemetry(records: list, output_dir: str = "dashboard/data"):
    """
    Save privacy-preserving telemetry data.
    No raw metrics, only presence and aggregates.
    """
    from garmin_integrity import DataIntegrity
    
    telemetry_file = f"{output_dir}/telemetry_{datetime.now().strftime('%Y%m%d')}.jsonl"
    
    # Create telemetry records
    telemetry_records = []
    for record in records:
        telemetry = DataIntegrity.create_telemetry_record(record, auto_run=False)
        telemetry_records.append(telemetry)
    
    # Use atomic write for telemetry
    if atomic_append_jsonl(telemetry_records, telemetry_file):
        logger.info(f"Telemetry saved to {telemetry_file}")
    else:
        logger.error(f"Failed to save telemetry to {telemetry_file}")

def main():
    """Main function to fetch Garmin data."""
    # Load credentials from environment
    from dotenv import load_dotenv
    load_dotenv()
    
    email = os.getenv('GARMIN_EMAIL')
    password = os.getenv('GARMIN_PASSWORD')
    
    if not email or not password:
        logger.error("GARMIN_EMAIL and GARMIN_PASSWORD must be set in .env file")
        sys.exit(1)
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Fetch wellness data from Garmin Connect')
    parser.add_argument('--days', type=int, default=30, 
                       help='Number of days to fetch (default: 30)')
    parser.add_argument('--output', type=str, default='dashboard/data/garmin_wellness.jsonl',
                       help='Output file path (default: dashboard/data/garmin_wellness.jsonl)')
    parser.add_argument('--date', type=str, 
                       help='Fetch specific date (YYYY-MM-DD)')
    args = parser.parse_args()
    
    # Phase 3: Battery safeguard check (AC4)
    if should_skip_battery():
        logger.info("Skipping fetch due to low battery")
        sys.exit(0)
    
    # Create fetcher and connect
    fetcher = GarminWellnessFetcher(email, password)
    if not fetcher.connect():
        sys.exit(1)
    
    # Fetch data
    if args.date:
        # Fetch specific date
        date = datetime.strptime(args.date, "%Y-%m-%d")
        records = [fetcher.fetch_daily_data(date)]
        records = [r for r in records if r]  # Filter None values
    else:
        # Fetch last N days
        logger.info(f"Fetching last {args.days} days of data...")
        records = fetcher.fetch_last_n_days(args.days)
    
    if not records:
        logger.error("No data fetched")
        sys.exit(1)
    
    # Save to file atomically
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    # Use atomic write to prevent corruption
    from utils.file_utils import atomic_write_jsonl
    if atomic_write_jsonl(records, args.output):
        logger.info(f"Successfully saved {len(records)} records to {args.output}")
    else:
        logger.error(f"Failed to save records to {args.output}")
        sys.exit(1)
    
    # Save telemetry (privacy-preserving)
    save_telemetry(records)
    
    # Run integrity checks
    from garmin_integrity import run_integrity_checks
    integrity_results = run_integrity_checks(args.output)
    
    # Print summary
    print("\n📊 Wellness Data Summary:")
    print(f"   Records fetched: {len(records)}")
    if records:
        scores = [r['score'] for r in records]
        print(f"   Average score: {sum(scores)/len(scores):.1f}")
        print(f"   Best day: {max(scores)}")
        print(f"   Worst day: {min(scores)}")
        print(f"   Data completeness: {integrity_results['completeness_avg']:.1f}%")
        print(f"\n✅ Data ready for ingestion: {args.output}")
        print(f"   Run: python3 dashboard/scripts/ingest_influxdb.py {args.output}")
        
        if integrity_results['invalid_records'] > 0:
            print(f"\n⚠️ Warning: {integrity_results['invalid_records']} invalid records found")
            print("   Run: python3 dashboard/scripts/garmin_integrity.py " + args.output)

if __name__ == "__main__":
    main()