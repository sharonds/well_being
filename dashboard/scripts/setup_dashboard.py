#!/usr/bin/env python3
"""Complete dashboard setup script.
Orchestrates the full dashboard setup process:
1. Generate synthetic data
2. Validate records  
3. Ingest into InfluxDB
4. Provision Grafana dashboard

Usage:
  PYTHONPATH=. python3 dashboard/scripts/setup_dashboard.py

Prerequisites:
- InfluxDB running on localhost:8086
- Grafana running on localhost:3000  
- .env configured with tokens and credentials
- pip install influxdb-client requests
"""
from __future__ import annotations
import subprocess, sys, pathlib, tempfile, os
import time

def run_command(cmd: list[str], description: str, required: bool = True) -> bool:
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
        if required:
            print(f"   This step is required - stopping setup")
        return False

def check_prerequisites() -> bool:
    """Check if all prerequisites are met."""
    print("🔍 Checking prerequisites...")
    
    # Check .env file
    env_path = pathlib.Path(".env")
    if not env_path.exists():
        print("❌ Missing .env file")
        print("   Copy .env.example and configure INFLUXDB_TOKEN, GRAFANA_ADMIN_PASSWORD")
        return False
    print("✅ .env file found")
    
    # Check Python dependencies
    try:
        import influxdb_client, requests
        print("✅ Python dependencies available")
    except ImportError as e:
        print(f"❌ Missing Python dependencies: {e}")
        print("   Install with: pip install influxdb-client requests")
        return False
    
    return True

def main():
    print("🚀 Well-Being Dashboard Complete Setup")
    print("=" * 50)
    
    # Check prerequisites
    if not check_prerequisites():
        return 1
    
    # Use temp file for synthetic data
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as tmp:
        tmp_path = pathlib.Path(tmp.name)
    
    try:
        print(f"\n📊 Setting up complete dashboard pipeline...")
        
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
        
        print("\n⏳ Waiting 3 seconds for InfluxDB to process data...")
        time.sleep(3)
        
        # Step 4: Provision Grafana dashboard
        if not run_command([
            "python3", "dashboard/scripts/provision_grafana.py"
        ], "Step 4: Provision Grafana dashboard", required=False):
            print("⚠️  Dashboard provisioning failed, but data is in InfluxDB")
            print("   You can manually import dashboard/grafana/wellbeing-dashboard.json")
        
        print("\n" + "=" * 50)
        print("✅ DASHBOARD SETUP COMPLETE!")
        print("=" * 50)
        
        print(f"\n📊 What's been created:")
        print(f"   • 30 days of synthetic well-being data")
        print(f"   • InfluxDB measurements: wb_score, wb_contrib, wb_quality")
        print(f"   • 4 baseline Grafana panels provisioned")
        
        print(f"\n🎯 Next steps:")
        print(f"   1. Access dashboard: http://localhost:3000/d/wellbeing/wellbeing-dashboard")
        print(f"   2. Complete security checklist before real data ingestion")
        print(f"   3. Replace synthetic export with real Garmin API calls")
        
        print(f"\n🔒 Security reminders:")
        print(f"   • All data is currently synthetic (safe)")
        print(f"   • Review dashboard_security_checklist.md before real data")
        print(f"   • Change default Grafana/InfluxDB passwords")
        
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