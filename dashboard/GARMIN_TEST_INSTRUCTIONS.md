# 🔐 Garmin Connection Test Instructions

Since your Garmin account appears to have MFA enabled, you'll need to run the test interactively.

## Option 1: Test Connection (Recommended)

Open a terminal and run:
```bash
cd ~/well_being
python3 dashboard/scripts/test_garmin_mfa.py
```

When prompted for MFA code, enter the 6-digit code from your authenticator app.

## Option 2: Disable MFA Temporarily

1. Log in to https://connect.garmin.com
2. Go to Account Settings → Security
3. Temporarily disable 2FA
4. Run the test: `python3 dashboard/scripts/test_garmin_connection.py`
5. Re-enable 2FA after testing

## Option 3: Use Garmin Connect App Token (Advanced)

Some users have success using app-specific passwords:
1. Log in to Garmin Connect
2. Generate an app-specific password
3. Use that instead of your regular password

## What Success Looks Like

When connection works, you'll see:
```
✅ Successfully connected!
👤 User Information:
   Name: Sharon
📊 Today's Data (2025-08-13):
   Steps: 5,432
   Resting HR: 58 bpm
   Sleep: 7.2 hours
   Stress: 35/100
```

## After Successful Connection

1. **Fetch your data:**
   ```bash
   python3 dashboard/scripts/fetch_garmin_data.py --days 7
   ```

2. **Check data integrity:**
   ```bash
   python3 dashboard/scripts/garmin_integrity.py dashboard/data/garmin_wellness.jsonl
   ```

3. **Ingest to InfluxDB:**
   ```bash
   python3 dashboard/scripts/ingest_influxdb.py dashboard/data/garmin_wellness.jsonl
   ```

4. **View in Grafana:**
   Open http://localhost:3001

## Troubleshooting

### "Invalid credentials"
- Double-check email and password in `.env`
- Try logging in at connect.garmin.com to verify

### "Too many requests"
- Garmin has rate limits
- Wait 15 minutes and try again

### "No data"
- Sync your Garmin device first
- Data may take time to appear after activities

## Privacy Note

Your credentials are stored locally in `.env` and never transmitted except to Garmin's official API. The telemetry we generate contains NO raw health metrics - only presence flags and aggregated scores.