# Runbook: Ingestion Failures

## Alert: Data Ingestion Stale

### Symptoms
- Alert: "🔄 Data Ingestion Stale"
- Data is >2 days behind current date
- No new records being added

### Impact
- Outdated wellness scores
- Missing historical data
- Degraded user experience

### Immediate Actions (< 5 minutes)

1. **Check Ingestion Status**
   ```bash
   python3 dashboard/scripts/ops/metrics_exporter.py --format json | \
     jq '.ingestion'
   ```

2. **Check Last Successful Fetch**
   ```bash
   ls -la dashboard/data/*.jsonl | tail -5
   tail -1 dashboard/data/garmin_wellness.jsonl
   ```

### Diagnosis (< 15 minutes)

1. **Test Garmin Connection**
   ```bash
   python3 dashboard/scripts/test_garmin_connection.py
   ```

2. **Check for Errors**
   ```bash
   # Check recent GitHub Actions logs
   gh run list --workflow="Daily Operations" --limit 5
   
   # Look for fetch errors
   gh run view <latest-run-id> --log | grep -i error
   ```

3. **Common Causes**
   - Garmin API down
   - MFA token expired  
   - Account locked/suspended
   - Network connectivity
   - Disk space issues

### Resolution Steps

#### If Garmin API Issue:
1. **Check Garmin Status**
   - Try logging into Garmin Connect manually
   - Check: https://connect.garmin.com/status

2. **Wait and Retry**
   ```bash
   # Wait 1 hour and retry
   sleep 3600
   python3 dashboard/scripts/fetch_garmin_data.py --date $(date -I)
   ```

#### If Authentication Issue:
1. **Test Login**
   ```bash
   # Interactive test with MFA
   python3 dashboard/scripts/test_garmin_mfa.py
   ```

2. **Update Credentials**
   ```bash
   # If password changed
   gh secret set GARMIN_PASSWORD
   
   # If MFA required
   ./dashboard/scripts/fetch_with_mfa.sh
   ```

#### If Disk Space:
1. **Check Space**
   ```bash
   df -h dashboard/data/
   ```

2. **Apply Retention Policy**
   ```bash
   # Force cleanup of old data
   python3 dashboard/scripts/phase3/retention_policy.py \
     --days 14 \
     --telemetry-dir dashboard/data
   ```

#### If Network Issue:
1. **Test Connectivity**
   ```bash
   curl -I https://connect.garmin.com
   ping -c 5 connect.garmin.com
   ```

2. **Check Firewall/Proxy**
   - Verify no blocking rules
   - Check proxy settings if applicable

### Manual Recovery

1. **Manual Fetch for Missing Dates**
   ```bash
   # Fetch last 7 days
   for i in {0..6}; do
     date=$(date -I -d "$i days ago")
     echo "Fetching $date..."
     python3 dashboard/scripts/fetch_garmin_data.py --date $date
   done
   ```

2. **Verify Ingestion**
   ```bash
   # Check new records
   tail -10 dashboard/data/garmin_wellness.jsonl
   
   # Run integrity check
   python3 dashboard/scripts/phase3/integrity_monitor.py \
     dashboard/data/garmin_wellness.jsonl --days 7
   ```

3. **Update Metrics**
   ```bash
   python3 dashboard/scripts/ops/metrics_exporter.py --save
   ```

### Monitoring Recovery

1. **Watch Next Auto-fetch**
   ```bash
   # Monitor next daily run
   gh workflow run "Daily Operations"
   gh run watch
   ```

2. **Verify Data Currency**
   ```bash
   # After 24 hours
   python3 dashboard/scripts/ops/metrics_exporter.py --format json | \
     jq '.ingestion.days_behind'
   ```

### Prevention

1. **Add Redundancy**
   - Implement retry logic with exponential backoff
   - Add alternative data sources

2. **Improve Monitoring**
   - Alert on first missed day (not just >2)
   - Add Garmin API health check

3. **Regular Maintenance**
   - Test authentication weekly
   - Monitor disk usage trends
   - Keep dependencies updated

### Post-Incident

1. **Log Incident**
   ```bash
   echo "{\"date\": \"$(date -I)\", \"type\": \"ingestion\", \"gap_days\": X, \"cause\": \"...\", \"resolution\": \"...\"}" >> docs/incident_log.jsonl
   ```

2. **Backfill if Needed**
   ```bash
   # Fetch missing date range
   python3 dashboard/scripts/fetch_garmin_data.py \
     --start-date 2025-08-10 \
     --end-date 2025-08-13
   ```

3. **Update Documentation**
   - Note any new failure patterns
   - Update credentials rotation schedule

### Related Documentation
- [Fetch Garmin Data](../../dashboard/scripts/fetch_garmin_data.py)
- [Ingestion Pipeline](../../dashboard/scripts/ingest_influxdb.py)
- [SLOs](../SLOs.md)

### Contact
- **Owner**: Platform Team
- **Slack**: #wellness-alerts
- **Escalation**: Create GitHub Issue with `ingestion` label

---
*Last Updated: 2025-08-13*