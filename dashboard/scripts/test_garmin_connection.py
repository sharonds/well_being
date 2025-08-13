#!/usr/bin/env python3
"""
Test Garmin Connect connection and show available data.
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from garminconnect import Garmin

# Load environment variables
load_dotenv()

def test_connection():
    """Test Garmin Connect connection and show sample data."""
    email = os.getenv('GARMIN_EMAIL')
    password = os.getenv('GARMIN_PASSWORD')
    
    if not email or not password or email == 'your.email@example.com':
        print("❌ Please update GARMIN_EMAIL and GARMIN_PASSWORD in .env file")
        print("   Current values are placeholders")
        return False
    
    print(f"🔐 Testing connection for: {email}")
    
    try:
        # Connect to Garmin
        print("📡 Connecting to Garmin Connect...")
        client = Garmin(email, password)
        client.login()
        print("✅ Successfully connected!")
        
        # Get user info
        print("\n👤 User Information:")
        user_info = client.get_full_name()
        print(f"   Name: {user_info}")
        
        # Get today's data
        today = datetime.now().strftime("%Y-%m-%d")
        print(f"\n📊 Today's Data ({today}):")
        
        # Steps
        try:
            steps_data = client.get_steps_data(today)
            if steps_data:
                print(f"   Steps: {steps_data[0]['steps']:,}")
        except:
            print("   Steps: No data")
        
        # Heart Rate
        try:
            hr_data = client.get_heart_rates(today)
            if hr_data and 'restingHeartRate' in hr_data:
                print(f"   Resting HR: {hr_data['restingHeartRate']} bpm")
        except:
            print("   Resting HR: No data")
        
        # Sleep
        try:
            sleep_data = client.get_sleep_data(today)
            if sleep_data and 'dailySleepDTO' in sleep_data:
                sleep_seconds = sleep_data['dailySleepDTO'].get('sleepTimeSeconds', 0)
                sleep_hours = round(sleep_seconds / 3600, 1)
                print(f"   Sleep: {sleep_hours} hours")
        except:
            print("   Sleep: No data")
        
        # Stress
        try:
            stress_data = client.get_stress_data(today)
            if stress_data and isinstance(stress_data, list) and len(stress_data) > 0:
                stress_values = [s.get('stressLevel', 0) for s in stress_data 
                               if s.get('stressLevel') is not None and s.get('stressLevel') > 0]
                if stress_values:
                    avg_stress = int(sum(stress_values) / len(stress_values))
                    print(f"   Stress: {avg_stress}/100")
        except:
            print("   Stress: No data")
        
        print("\n✅ Connection test successful!")
        print("   You can now run: python3 dashboard/scripts/fetch_garmin_data.py")
        return True
        
    except Exception as e:
        print(f"\n❌ Connection failed: {e}")
        print("\nTroubleshooting:")
        print("1. Check your email and password are correct")
        print("2. Make sure 2FA is not enabled on your Garmin account")
        print("3. Try logging in at https://connect.garmin.com to verify credentials")
        return False

if __name__ == "__main__":
    test_connection()