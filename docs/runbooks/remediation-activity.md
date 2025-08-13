# Runbook: High Remediation Activity

## Alert: High Remediation Activity (7d)

### Symptoms
- Alert: "🔧 High Remediation Activity"
- More than 10 remediations in the last 7 days
- Frequent integrity corrections or quarantines

### Impact
- Sign of persistent upstream quality issues
- Increased quarantine volume and potential data loss
- Risk of masking a systemic defect (ingestion, scoring, schema)

### Immediate Actions (< 5 minutes)

1. Check remediation metrics
```bash
python3 dashboard/scripts/ops/metrics_exporter.py --format json | \
  jq '.remediation'
```

2. Inspect recent remediations
```bash
# If log exists
jq -r '.remediations[-20:]' dashboard/data/remediation_log.json || true
```

### Diagnosis (< 20 minutes)

1. Categorize errors
```bash
# Generate integrity report with categories
python3 dashboard/scripts/phase3/integrity_monitor.py \
  dashboard/data/*.jsonl --days 14 --report | jq '.failure_rates["14_days"].remediation'
```

2. Common causes
- Formula drift (score/band mismatches)
- Schema/version inconsistencies (pre-normalization data)
- Upstream ingestion anomalies (partial records)
- New data fields leaking into telemetry (privacy scan)

3. Cross-check quality gates
```bash
# Verify CI gates are green
ls .github/workflows/quality-gates.yml
```

### Resolution Steps

1. Auto-remediate deterministics
```bash
# Dry run first
python3 dashboard/scripts/phase3/integrity_auto_remediate.py \
  dashboard/data/garmin_wellness.jsonl --dry-run

# Apply if safe
python3 dashboard/scripts/phase3/integrity_auto_remediate.py \
  dashboard/data/garmin_wellness.jsonl
```

2. Quarantine non-deterministics
- Ensure QUARANTINE_ENABLED=true
- Review quarantine files under dashboard/data/quarantine

3. Address root cause
- If formula drift: lock compute via score.engine and add boundary tests
- If schema issues: run duplicate guard validation and migrate/normalize
- If ingestion: fix fetcher transformation or retry/backfill

### Prevention
- Keep band mapping and scoring centralized (score/engine.py)
- Enforce atomic writes to prevent partial records
- Tighten privacy scan and schema validation in CI
- Add specific detectors for recurring error types

### Post-Incident
```bash
# Log summary
echo "{\"date\": \"$(date -I)\", \"type\": \"remediation\", \"count_7d\": N, \"cause\": \"...\", \"actions\": \"...\"}" \
  >> docs/incident_log.jsonl
```

### Related
- Integrity Failures: docs/runbooks/integrity-failures.md
- SLOs: docs/SLOs.md
- Duplicate Guard: dashboard/scripts/duplicate_guard.py

---
Last Updated: 2025-08-13
