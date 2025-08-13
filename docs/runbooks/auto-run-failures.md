# Runbook: Auto-run Failures

## Alert: Auto-run Success Rate Below Target

### Symptoms
- Alert: "⚠️ Auto-run Success Rate Below Target"
- Success rate < 90% over 14-day window
- Manual runs exceeding automated runs

### Impact
- Reduced automation effectiveness
- Stale data risk
- Manual intervention burden

### Immediate Actions (< 5 minutes)

1. **Check Current Rate**
   ```bash
   python3 dashboard/scripts/ops/metrics_exporter.py --format json | \
     jq '.auto_run.success_rate_pct'
   ```

2. **Verify GitHub Actions Status**
   ```bash
   gh workflow list --repo sharonds/well_being
   gh run list --workflow="Daily Operations" --limit 5
   ```

### Diagnosis (< 15 minutes)

1. **Check Recent Runs**
   ```bash
   # View recent workflow runs
   gh run list --workflow="Daily Operations" --limit 10
   
   # Check for failures
   gh run view <run-id>
   ```

2. **Common Failure Causes**
   - GitHub Actions outage
   - Credential expiration (Garmin API)
   - Rate limiting
   - Network issues
   - Battery safeguard triggered

3. **Check Logs**
   ```bash
   # Download workflow logs
   gh run download <run-id> -n daily-metrics-<run-id>
   cat metrics.json | jq '.auto_run'
   ```

### Resolution Steps

#### If GitHub Actions Issue:
1. **Check GitHub Status**
   - Visit: https://www.githubstatus.com/
   - Check Actions specifically

2. **Retry Failed Runs**
   ```bash
   gh run rerun <run-id>
   ```

3. **Manual Trigger**
   ```bash
   gh workflow run "Daily Operations"
   ```

#### If Credential Issue:
1. **Check Garmin Credentials**
   ```bash
   # Test connection
   python3 dashboard/scripts/test_garmin_connection.py
   ```

2. **Update Secrets if Needed**
   - Go to: Settings → Secrets → Actions
   - Update GARMIN_EMAIL and GARMIN_PASSWORD

#### If Rate Limiting:
1. **Check Rate Limit Status**
   ```bash
   # In logs, look for rate limit errors
   grep -i "rate" workflow_logs.txt
   ```

2. **Adjust Schedule**
   - Edit `.github/workflows/daily-ops.yml`
   - Change cron schedule to different time

#### If Battery Safeguard:
1. **Check Battery Levels**
   ```bash
   # Check if battery safeguard is triggering
   BATTERY_LEVEL=10 python3 dashboard/scripts/phase3/battery_safeguard.py
   ```

2. **Temporarily Adjust Threshold**
   ```bash
   export BATTERY_MIN_PERCENT=5
   ```

### Monitoring Recovery

1. **Track Next Runs**
   ```bash
   # Watch next scheduled run
   gh run watch
   ```

2. **Verify Metrics Improvement**
   ```bash
   # After 24 hours, check if rate improving
   python3 dashboard/scripts/ops/metrics_exporter.py --format json | \
     jq '.auto_run'
   ```

### Prevention

1. **Add Redundancy**
   - Consider backup scheduling mechanism
   - Add retry logic to workflows

2. **Improve Monitoring**
   - Add workflow failure alerts
   - Monitor GitHub Actions health

3. **Regular Maintenance**
   - Rotate credentials quarterly
   - Test backup procedures monthly

### Post-Incident

1. **Log Incident**
   ```bash
   echo "{\"date\": \"$(date -I)\", \"type\": \"auto_run\", \"cause\": \"...\", \"resolution\": \"...\", \"downtime\": \"XX hours\"}" >> docs/incident_log.jsonl
   ```

2. **Update Automation**
   - Add resilience for discovered failure mode
   - Update retry logic if needed

### Related Documentation
- [Auto-run Tracker](../../dashboard/scripts/phase3/auto_run_tracker.py)
- [Daily Ops Workflow](../../.github/workflows/daily-ops.yml)
- [SLOs](../SLOs.md)

### Contact
- **Owner**: Platform Team
- **Slack**: #wellness-alerts
- **Escalation**: Create GitHub Issue with `automation` label

---
*Last Updated: 2025-08-13*