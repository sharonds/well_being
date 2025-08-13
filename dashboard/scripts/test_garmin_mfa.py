#!/usr/bin/env python3
"""
Test Garmin Connect connection with MFA support.
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from garminconnect import Garmin
import getpass

# Load environment variables
load_dotenv()

def test_connection_with_mfa():
    """Test Garmin Connect connection with MFA support."""
    email = os.getenv('GARMIN_EMAIL')
    password = os.getenv('GARMIN_PASSWORD')
    
    if not email or not password or email == 'your.email@example.com':
        print("❌ Please update GARMIN_EMAIL and GARMIN_PASSWORD in .env file")
        return False
    
    print(f"🔐 Testing connection for: {email}")
    
    try:
        # Connect to Garmin
        print("📡 Connecting to Garmin Connect...")
        client = Garmin(email, password)
        
        try:
            # Try regular login first
            client.login()
            print("✅ Successfully connected (no MFA)!")
        except Exception as e:
            if "MFA" in str(e) or "code" in str(e).lower():
                print("\n📱 MFA detected. Please enter your 6-digit code from your authenticator app.")
                mfa_code = input("MFA code: ").strip()
                
                # Try login with MFA
                client = Garmin(email, password)
                client.login(mfa_code)
                print("✅ Successfully connected with MFA!")
            else:
                raise e
        
        # Get user info
        print("\n👤 User Information:")
        try:
            user_info = client.get_full_name()
            print(f"   Name: {user_info}")
        except:
            print("   Name: (not available)")
        
        # Get today's data
        today = datetime.now().strftime("%Y-%m-%d")
        print(f"\n📊 Today's Data ({today}):")
        
        # Steps
        try:
            steps_data = client.get_steps_data(today)
            if steps_data and len(steps_data) > 0:
                print(f"   Steps: {steps_data[0].get('steps', 0):,}")
            else:
                print("   Steps: No data yet today")
        except Exception as e:
            print(f"   Steps: Error - {str(e)[:50]}")
        
        # Heart Rate
        try:
            hr_data = client.get_heart_rates(today)
            if hr_data and 'restingHeartRate' in hr_data:
                print(f"   Resting HR: {hr_data['restingHeartRate']} bpm")
            else:
                print("   Resting HR: No data yet today")
        except:
            print("   Resting HR: No data")
        
        # Sleep (from last night)
        try:
            sleep_data = client.get_sleep_data(today)
            if sleep_data and 'dailySleepDTO' in sleep_data:
                sleep_seconds = sleep_data['dailySleepDTO'].get('sleepTimeSeconds', 0)
                sleep_hours = round(sleep_seconds / 3600, 1)
                print(f"   Sleep: {sleep_hours} hours")
            else:
                print("   Sleep: No data yet")
        except:
            print("   Sleep: No data")
        
        # Stress
        try:
            stress_data = client.get_stress_data(today)
            if stress_data and isinstance(stress_data, list) and len(stress_data) > 0:
                # Get average of non-negative values
                stress_values = [s.get('stressLevel', 0) for s in stress_data 
                               if s.get('stressLevel') is not None and s.get('stressLevel') >= 0]
                if stress_values:
                    avg_stress = int(sum(stress_values) / len(stress_values))
                    print(f"   Stress: {avg_stress}/100")
                else:
                    print("   Stress: No valid readings yet")
            else:
                print("   Stress: No data yet")
        except:
            print("   Stress: No data")
        
        print("\n✅ Connection test successful!")
        print("\n📝 Next steps:")
        print("1. Run fetch script: python3 dashboard/scripts/fetch_garmin_data.py")
        print("2. Ingest to InfluxDB: python3 dashboard/scripts/ingest_influxdb.py dashboard/data/garmin_wellness.jsonl")
        print("3. View dashboard: http://localhost:3001")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Connection failed: {e}")
        print("\nTroubleshooting:")
        print("1. Check your email and password are correct")
        print("2. If using MFA, make sure you have your authenticator app ready")
        print("3. Try logging in at https://connect.garmin.com to verify credentials")
        print("4. Check if your account is locked (too many failed attempts)")
        return False

if __name__ == "__main__":
    success = test_connection_with_mfa()
    sys.exit(0 if success else 1)