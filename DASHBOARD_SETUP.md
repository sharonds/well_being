# Dashboard Setup Guide

## Current Status: ✅ OPERATIONAL
- **Grafana**: Running at http://localhost:3001
- **InfluxDB**: Running at http://localhost:8087
- **Data**: 30 days of test data successfully visualized

## Quick Start

### 1. Start Infrastructure
```bash
docker-compose up -d
```

### 2. Access Dashboard
- URL: http://localhost:3001
- Login: `wellness_admin` / `wellbeing_secure_password`
- Dashboard: "Wellness Simple Dashboard"

### 3. Add Data

#### Option A: Test Data (Already Done)
```bash
# Generate test data
PYTHONPATH=. python3 dashboard/scripts/export_historical.py dashboard/data/test_export.jsonl

# Validate
PYTHONPATH=. python3 dashboard/scripts/validate_daily_records.py dashboard/data/test_export.jsonl

# Ingest
PYTHONPATH=. python3 dashboard/scripts/ingest_influxdb.py dashboard/data/test_export.jsonl
```

#### Option B: Manual Entry
```bash
# Interactive entry for real data
python3 dashboard/scripts/manual_entry.py

# Then validate and ingest
PYTHONPATH=. python3 dashboard/scripts/validate_daily_records.py dashboard/data/real_manual_entry.jsonl
PYTHONPATH=. python3 dashboard/scripts/ingest_influxdb.py dashboard/data/real_manual_entry.jsonl
```

#### Option C: Garmin API (Future)
```bash
# Install library
python3 -m pip install garminconnect

# Run fetch script (to be created)
python3 dashboard/scripts/fetch_garmin_daily.py
```

## Configuration

### Environment Variables (.env)
```
GRAFANA_ADMIN_USER=wellness_admin
GRAFANA_ADMIN_PASSWORD=wellbeing_secure_password
GRAFANA_PORT=3001
INFLUXDB_PORT=8087
INFLUXDB_URL=http://localhost:8087
INFLUXDB_TOKEN=p0NIqi1Q5V6U1phBOyFc3S5CYIvWBvqf7IJHyFchQBxYAFDYGAW33-aQUQPMJJvr8NKckRKhZbc6usv7EMP-Gw==
INFLUXDB_ORG=local
INFLUXDB_BUCKET=metrics
```

### InfluxDB Datasource in Grafana
- **URL**: http://wellbeing-influxdb:8086
- **Organization**: local
- **Token**: (see .env)
- **Bucket**: metrics
- **Query Language**: Flux

## Troubleshooting

### No Data Showing?
1. Check datasource connection in Grafana
2. Verify data in InfluxDB:
```bash
curl -X POST 'http://localhost:8087/api/v2/query?org=local' \
  -H "Authorization: Token [YOUR_TOKEN]" \
  -H 'Content-Type: application/vnd.flux' \
  -d 'from(bucket: "metrics") |> range(start: -30d) |> limit(n: 5)'
```

### Container Issues?
```bash
# Check status
docker ps

# View logs
docker logs wellbeing-grafana
docker logs wellbeing-influxdb

# Restart
docker-compose restart
```

### Reset Everything?
```bash
docker-compose down
docker volume rm wellbeing_influxdb-data wellbeing_grafana-data
docker-compose up -d
# Then re-run data ingestion
```

## Next Steps

1. **Add Real Data**: Use manual entry or Garmin API
2. **Enhance Dashboard**: Add more visualization panels
3. **Automate Updates**: Set up daily data fetch
4. **Monitor Trends**: Track wellness patterns over time

## Files Reference

- `docker-compose.yml` - Infrastructure definition
- `dashboard/grafana/simple-dashboard.json` - Working dashboard
- `dashboard/scripts/` - Data processing scripts
- `dashboard/data/` - Data files (JSONL format)
- `.env` - Configuration (DO NOT COMMIT)