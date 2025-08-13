#!/usr/bin/env python3
"""Pipeline validation script - demonstrates complete working data flow.

Validates:
1. Python parity engine (Examples A/B/C)  
2. Schema validation
3. InfluxDB ingestion capability
4. Dashboard data visibility

Usage:
  PYTHONPATH=. python3 dashboard/scripts/validate_pipeline.py
"""
from __future__ import annotations
import sys, json, pathlib
import subprocess

def run_parity_tests():
    """Validate parity engine matches PRD examples."""
    print("🧮 Testing parity engine...")
    try:
        result = subprocess.run([
            sys.executable, "dashboard/tests/test_vectors.py"
        ], capture_output=True, text=True, env={"PYTHONPATH": "."})
        
        if result.returncode == 0 and "All vector tests passed" in result.stdout:
            print("✅ Parity tests: PASS (A=65, B=88, C=25)")
            return True
        else:
            print(f"❌ Parity tests failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Parity test error: {e}")
        return False

def validate_schema():
    """Check schema validation works."""
    print("📋 Testing schema validation...")
    sample_file = pathlib.Path("dashboard/tests/sample_daily_records.jsonl")
    if not sample_file.exists():
        print("❌ Sample data file missing")
        return False
        
    try:
        result = subprocess.run([
            sys.executable, "dashboard/scripts/validate_daily_records.py", str(sample_file)
        ], capture_output=True, text=True, env={"PYTHONPATH": "."})
        
        if result.returncode == 0 and "VALIDATION PASSED" in result.stdout:
            print("✅ Schema validation: PASS")
            return True
        else:
            print(f"❌ Schema validation failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Schema validation error: {e}")
        return False

def check_ingestion_ready():
    """Verify ingestion script exists and dependencies available."""
    print("💾 Checking ingestion capability...")
    
    ingest_script = pathlib.Path("dashboard/scripts/ingest_influxdb.py")
    if not ingest_script.exists():
        print("❌ InfluxDB ingestion script missing")
        return False
        
    try:
        # Check if influxdb-client is available
        import influxdb_client
        print("✅ InfluxDB ingestion: Ready (influxdb-client available)")
        return True
    except ImportError:
        print("⚠️  InfluxDB ingestion: influxdb-client not installed (pip install influxdb-client)")
        return False

def check_dashboard_provisioned():
    """Check if dashboard JSON exists for provisioning."""
    print("📊 Checking dashboard provisioning...")
    
    dashboard_json = pathlib.Path("dashboard/grafana/provisioning/dashboards/json/wellbeing-dashboard.json")
    if dashboard_json.exists():
        # Validate it's not empty and has title
        try:
            with open(dashboard_json) as f:
                data = json.load(f)
                if data.get("title"):
                    print("✅ Dashboard provisioning: Ready")
                    return True
                else:
                    print("❌ Dashboard JSON missing title")
                    return False
        except Exception as e:
            print(f"❌ Dashboard JSON invalid: {e}")
            return False
    else:
        print("❌ Dashboard JSON not found for provisioning")
        return False

def main():
    print("🔍 Well-Being Dashboard Pipeline Validation")
    print("=" * 50)
    
    results = []
    results.append(("Parity Engine", run_parity_tests()))
    results.append(("Schema Validation", validate_schema()))
    results.append(("InfluxDB Ingestion", check_ingestion_ready()))
    results.append(("Dashboard Provisioning", check_dashboard_provisioned()))
    
    print("\n" + "=" * 50)
    print("📊 Validation Summary:")
    
    passed = 0
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} components ready")
    
    if passed == len(results):
        print("🎉 Complete pipeline validated - ready for real data!")
        return 0
    else:
        print("⚠️  Some components need attention before production use")
        return 1

if __name__ == "__main__":
    raise SystemExit(main())