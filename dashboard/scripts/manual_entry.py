#!/usr/bin/env python3
"""
Manual entry helper for quick real data input
Phase 1: Bridge to real data
"""
import json
from datetime import datetime

def create_daily_record(date, steps, resting_hr, sleep_hours=None, stress=None):
    """Create a single daily record in dashboard format"""
    
    # Calculate readiness score (matching wearable formula)
    steps_norm = min(steps / 12000, 1.0)
    hr_norm = max(0, (80 - resting_hr) / 40) if resting_hr else 0
    sleep_norm = min(sleep_hours / 8, 1.0) if sleep_hours else 0
    stress_norm = max(0, (100 - stress) / 100) if stress else 0
    
    # Calculate score based on available metrics
    if sleep_hours and stress:
        score = (steps_norm * 0.4) + (hr_norm * 0.3) + (sleep_norm * 0.2) + (stress_norm * 0.1)
    else:
        score = (steps_norm * 0.7) + (hr_norm * 0.3)
    
    readiness_score = int(score * 100)
    
    # Build record
    record = {
        "date": date,
        "steps": steps,
        "resting_hr": resting_hr,
        "sleep_hours": sleep_hours,
        "stress_level": stress,
        "readiness_score": readiness_score,
        "metadata": {
            "device": "manual_entry",
            "computed_at": datetime.now().strftime("%H:%M:%S"),
            "mode": "manual"
        }
    }
    
    # Calculate contributions
    contributions = {}
    contributions["steps"] = round(steps_norm * 0.4, 3)
    contributions["resting_hr"] = round(hr_norm * 0.3, 3)
    if sleep_hours:
        contributions["sleep"] = round(sleep_norm * 0.2, 3)
    if stress:
        contributions["stress"] = round(stress_norm * 0.1, 3)
    
    record["contributions"] = contributions
    
    return record

def main():
    """Interactive manual entry"""
    print("=== Manual Wellness Data Entry ===")
    print("Enter your wellness data for the past 3 days")
    print("(Leave blank for missing values)\n")
    
    records = []
    
    for i in range(3):
        print(f"\nDay {i+1}:")
        date = input("  Date (YYYY-MM-DD): ").strip()
        steps = int(input("  Steps: "))
        resting_hr = int(input("  Resting HR: "))
        
        sleep_input = input("  Sleep hours (optional): ").strip()
        sleep_hours = float(sleep_input) if sleep_input else None
        
        stress_input = input("  Stress level 0-100 (optional): ").strip()
        stress = int(stress_input) if stress_input else None
        
        record = create_daily_record(date, steps, resting_hr, sleep_hours, stress)
        records.append(record)
        
        print(f"  → Readiness Score: {record['readiness_score']}")
    
    # Save to file
    output_file = "/Users/sharonsciammas/well_being/dashboard/data/real_manual_entry.jsonl"
    with open(output_file, 'w') as f:
        for record in records:
            f.write(json.dumps(record) + '\n')
    
    print(f"\n✅ Saved {len(records)} records to {output_file}")
    print("\nNext steps:")
    print("1. Validate: python3 dashboard/scripts/validate_daily_records.py dashboard/data/real_manual_entry.jsonl")
    print("2. Ingest: python3 dashboard/scripts/ingest_influxdb.py")
    print("3. View at: http://localhost:3001")

if __name__ == "__main__":
    main()