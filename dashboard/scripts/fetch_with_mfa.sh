#!/bin/bash

# Fetch Garmin data with MFA support
echo "🏃 Garmin Data Fetch Script"
echo "=========================="
echo ""
echo "This script will fetch your Garmin wellness data."
echo "You'll need your MFA code from your authenticator app."
echo ""

# Default to 7 days if not specified
DAYS=${1:-7}

echo "Fetching last $DAYS days of data..."
echo ""

# Run the Python script
python3 dashboard/scripts/fetch_garmin_data.py --days $DAYS

# Check if successful
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Data fetched successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Check integrity: python3 dashboard/scripts/garmin_integrity.py dashboard/data/garmin_wellness.jsonl"
    echo "2. Ingest to InfluxDB: python3 dashboard/scripts/ingest_influxdb.py dashboard/data/garmin_wellness.jsonl"
    echo "3. View dashboard: http://localhost:3001"
else
    echo ""
    echo "❌ Fetch failed. Please check your credentials and try again."
fi