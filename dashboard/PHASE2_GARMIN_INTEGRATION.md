# 📊 Phase 2: Garmin Connect Integration

## Overview
This phase replaces synthetic test data with real wellness data from Garmin Connect, enabling the dashboard to display your actual health metrics.

## ✅ What's Been Implemented

### 1. **Garmin Data Fetcher** (`fetch_garmin_data.py`)
- Connects to Garmin Connect API
- Fetches 4 key metrics:
  - **Steps**: Daily step count
  - **Resting Heart Rate**: From daily stats
  - **Sleep**: Hours of sleep (converted from seconds)
  - **Stress**: Average stress level (0-100)
- Calculates wellness scores using our formula
- Exports data in our standard JSON schema

### 2. **Connection Tester** (`test_garmin_connection.py`)
- Verifies credentials work
- Shows sample data from your account
- Helps troubleshoot connection issues

### 3. **Automated Pipeline Updates**
- GitHub Actions workflow now supports Garmin data
- Can be triggered manually or on schedule
- Requires `GARMIN_EMAIL` and `GARMIN_PASSWORD` secrets

## 🚀 Setup Instructions

### Step 1: Configure Credentials

Edit `.env` file and add your Garmin credentials:
```bash
GARMIN_EMAIL=your.actual@email.com
GARMIN_PASSWORD=your_actual_password
```

⚠️ **Important**: 
- Use your actual Garmin Connect credentials
- 2FA must be disabled on your Garmin account
- Never commit `.env` to git (it's in .gitignore)

### Step 2: Install Dependencies

```bash
pip install -r dashboard/requirements.txt
```

Or just the Garmin library:
```bash
pip install garminconnect python-dotenv
```

### Step 3: Test Connection

```bash
python3 dashboard/scripts/test_garmin_connection.py
```

You should see:
- ✅ Successfully connected!
- Your name from Garmin
- Today's metrics

### Step 4: Fetch Your Data

Fetch last 30 days:
```bash
python3 dashboard/scripts/fetch_garmin_data.py
```

Fetch specific number of days:
```bash
python3 dashboard/scripts/fetch_garmin_data.py --days 7
```

Fetch specific date:
```bash
python3 dashboard/scripts/fetch_garmin_data.py --date 2025-08-01
```

### Step 5: Ingest into InfluxDB

```bash
# Make sure Docker is running
docker-compose up -d

# Ingest the data
python3 dashboard/scripts/ingest_influxdb.py dashboard/data/garmin_wellness.jsonl
```

### Step 6: View in Grafana

Open http://localhost:3001 and see your real data!

## 🤖 GitHub Actions Setup

To enable automated daily fetching:

### 1. Add GitHub Secrets
Go to Settings → Secrets → Actions and add:
- `GARMIN_EMAIL`: Your Garmin email
- `GARMIN_PASSWORD`: Your Garmin password

### 2. Run Manually
```bash
gh workflow run dashboard-automation.yml \
  --field data_source=garmin_api \
  --field days_back=30
```

### 3. Daily Schedule
The workflow runs daily at 12pm UTC and fetches your latest data.

## 📊 Data Mapping

| Garmin Metric | Our Schema | Notes |
|--------------|------------|-------|
| steps | metrics.steps | Daily total |
| restingHeartRate | metrics.restingHeartRate | From daily stats |
| sleepTimeSeconds | metrics.sleepHours | Converted to hours |
| stressLevel | metrics.stress | Average for the day |

## 🧮 Wellness Score Calculation

The score (0-100) is calculated as:
- **Steps** (25 points): 10k+ = 25, 7.5k = 20, 5k = 15, 2.5k = 10
- **Resting HR** (25 points): <50 = 25, <60 = 20, <70 = 15, <80 = 10
- **Sleep** (25 points): 8h+ = 25, 7h = 20, 6h = 15, 5h = 10
- **Stress** (25 points): ≤25 = 25, ≤40 = 20, ≤55 = 15, ≤70 = 10

## 🔧 Troubleshooting

### Connection Failed
1. Check credentials in `.env`
2. Verify you can login at https://connect.garmin.com
3. Disable 2FA if enabled
4. Try the test script first

### No Data Retrieved
1. Check you have data for the requested dates
2. Sync your Garmin device recently
3. Try fetching just today: `--date $(date +%Y-%m-%d)`

### Import to InfluxDB Failed
1. Ensure Docker is running: `docker-compose up -d`
2. Check InfluxDB token in `.env`
3. Verify data file exists: `ls dashboard/data/*.jsonl`

## 📁 File Structure

```
dashboard/
├── scripts/
│   ├── fetch_garmin_data.py      # Main fetcher
│   ├── test_garmin_connection.py # Connection tester
│   ├── ingest_influxdb.py        # Data ingestion
│   └── validate_daily_records.py # Schema validator
├── data/
│   └── garmin_wellness.jsonl     # Fetched data
└── requirements.txt               # Python dependencies
```

## 🔒 Privacy & Integrity Features (NEW)

Based on security review, Phase 2 now includes:

### Data Integrity
- **Metrics presence mask**: Bitfield tracking which metrics are available
- **Score invariant validation**: Ensures scores are within bounds and consistent
- **Schema versioning**: Safe migration path for future updates
- **Formula hash tracking**: Detects scoring formula drift

### Privacy-First Telemetry
- **No raw metrics exported**: Only presence flags and aggregates
- **Telemetry records**: Date, score, band, completeness % only
- **Ring buffer storage**: Limited retention for privacy

### Timezone/DST Handling
- **20-hour minimum between fetches**: Prevents double-runs during DST
- **UTC timestamp tracking**: Timezone-agnostic scheduling
- **Duplicate run prevention**: Sentinel persistence

### Observability
- **Completeness tracking**: % of metrics present per day
- **Integrity checks**: Automatic validation on every fetch
- **CI/CD guards**: Phase 2/3 workflow prevents regression

## ✅ Phase 2 Complete!

With hardened Garmin integration, you now have:
1. Real wellness data from your Garmin device
2. Privacy-preserving telemetry (no raw metrics)
3. Automated integrity checks and validation
4. Timezone-safe fetching logic
5. Observable data completeness metrics

## 🎯 Next: Phase 3

Phase 3 will add:
- Automated daily ingestion pipeline
- Data quality monitoring
- Alert system for anomalies
- Enhanced visualizations
- Mobile-responsive dashboard

---

**Status**: Phase 2 COMPLETE ✅
**Issue**: #34
**Data Source**: Garmin Connect API (Real Data)