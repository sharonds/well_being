# Runbook: Integrity Failures

## Alert: Integrity Failure Rate Exceeded

### Symptoms
- Alert: "🚨 Integrity Failure Rate Exceeded"
- Integrity failure rate ≥ 1% over 14-day window
- Band mapping inconsistencies detected

### Impact
- Data quality degradation
- Incorrect wellness scores/bands
- User trust erosion

### Immediate Actions (< 5 minutes)

1. **Acknowledge Alert**
   ```bash
   # Check current integrity status
   python3 dashboard/scripts/phase3/integrity_monitor.py dashboard/data/*.jsonl --days 14
   ```

2. **Identify Failure Pattern**
   ```bash
   # Check recent remediation report
   cat dashboard/data/remediation_log.json | jq '.recent_errors'
   ```

### Resolution Steps (< 30 minutes)

1. **Run Auto-Remediation**
   ```bash
   # Dry run first to see what will be fixed
   python3 dashboard/scripts/phase3/integrity_auto_remediate.py \
     dashboard/data/garmin_wellness.jsonl --dry-run
   
   # If looks good, run actual remediation
   python3 dashboard/scripts/phase3/integrity_auto_remediate.py \
     dashboard/data/garmin_wellness.jsonl
   ```

2. **Verify Fix**
   ```bash
   # Re-run integrity check
   python3 dashboard/scripts/phase3/integrity_monitor.py dashboard/data/*.jsonl --days 14
   
   # Should see: "Integrity check passed"
   ```

3. **Check for Root Cause**
   - Formula drift: Check if scoring formula changed
   - Bad data ingestion: Check recent imports
   - Schema version mismatch: Check duplicate guard

### If Auto-Remediation Fails

1. **Manual Investigation**
   ```bash
   # Check specific failing records
   python3 -c "
   from dashboard.scripts.phase3.integrity_monitor import load_telemetry_records, validate_record_integrity
   records = load_telemetry_records('dashboard/data/garmin_wellness.jsonl')
   for r in records[-10:]:  # Check last 10
       valid, errors = validate_record_integrity(r)
       if not valid:
           print(f\"{r.get('date')}: {errors}\")
   "
   ```

2. **Manual Fix**
   ```bash
   # Use fix_integrity tool
   python3 dashboard/scripts/phase3/fix_integrity.py \
     dashboard/data/garmin_wellness.jsonl
   ```

3. **Escalate if Needed**
   - Create GitHub issue with error details
   - Tag platform team
   - Include integrity report output

### Prevention

1. **Check CI Gates**
   - Ensure quality-gates workflow is running
   - Verify no recent bypasses

2. **Review Recent Changes**
   ```bash
   git log --oneline -10 dashboard/
   ```

3. **Update Monitoring**
   - Consider lowering alert threshold if recurring
   - Add specific error pattern monitoring

### Post-Incident

1. **Document in Alert History**
   ```bash
   echo "{\"date\": \"$(date -I)\", \"type\": \"integrity\", \"resolution\": \"...\", \"time_to_resolve\": \"XX min\"}" >> docs/incident_log.jsonl
   ```

2. **Update This Runbook**
   - Add any new failure patterns discovered
   - Update resolution steps if needed

### Related Documentation
- [Integrity Monitor Source](../../dashboard/scripts/phase3/integrity_monitor.py)
- [Auto-Remediation Tool](../../dashboard/scripts/phase3/integrity_auto_remediate.py)
- [SLOs](../SLOs.md)

### Contact
- **Owner**: Platform Team
- **Slack**: #wellness-alerts
- **Escalation**: Create GitHub Issue

---
*Last Updated: 2025-08-13*