# Daily Operations Guide

## Overview

The Daily Operations workflow runs automatically at 8 AM UTC every day to monitor system health, remediate issues, and track burn-in progress for GA release readiness.

## Workflow Components

### 1. Integrity Check
- Validates data quality over the last 14 days
- Uses consistent telemetry file path across all steps
- Automatically creates test data if none exists (CI/test environments)
- Reports pass/fail status for downstream actions

### 2. Auto-Remediation
- Triggers only when integrity issues are detected
- Uses the same telemetry file as the integrity check
- Runs in dry-run mode during CI to prevent unintended changes
- Categorizes and fixes deterministic errors automatically

### 3. Retention Policy
- Applies 30-day data retention window
- Cleans up old telemetry and quarantine files
- Runs in dry-run mode during CI
- Configurable retention period via environment variables

### 4. Metrics Collection
- Exports operational metrics in JSON format
- Tracks integrity failure rate (14-day window)
- Monitors auto-run success rate
- Saves metrics for historical analysis

### 5. Alert Management
- Checks thresholds and sends alerts when breached
- Supports Slack webhook notifications
- Falls back to console output if webhook not configured
- Dry-run mode available for testing

### 6. Burn-in Tracker
- Monitors 30-day burn-in period progress
- Calculates days elapsed and remaining
- Reports GA readiness upon completion
- Configurable start date via GitHub variables

## File Path Resolution

The workflow intelligently resolves which telemetry file to use:

```bash
# Production scenario
if [ -f "dashboard/data/garmin_wellness.jsonl" ]; then
  TELEMETRY_FILE="dashboard/data/garmin_wellness.jsonl"
fi

# Test/CI scenario
if [ ! -f "$TELEMETRY_FILE" ]; then
  TELEMETRY_FILE="dashboard/data/test_telemetry.jsonl"
  # Create test data
fi
```

This ensures:
- Consistent data source across integrity and remediation steps
- No references to non-existent files
- Automatic test data generation in CI environments
- Single source of truth for telemetry processing

## Configuration

### Required Secrets
- `SLACK_WEBHOOK_URL`: Slack webhook for alert notifications (optional)

### Environment Variables
- `BURN_IN_START_DATE`: Start date for 30-day burn-in period (defaults to 2025-08-13)

### Workflow Dispatch
The workflow can be manually triggered with options:
- `dry_run`: Set to 'true' to prevent alert notifications

## Monitoring

### Daily Report
Each run generates a comprehensive report including:
- Current date and time
- Integrity failure rate (%)
- Auto-run success rate (%)
- Actions taken (remediation, retention, alerts)
- Burn-in progress status

### Artifacts
The workflow saves the following artifacts for 30 days:
- `metrics.json`: Complete operational metrics
- `integrity_report.txt`: Detailed integrity check results

## Alert Thresholds

| Metric | Threshold | Severity | Runbook |
|--------|-----------|----------|---------|
| Integrity Failure Rate | ≥1% | Critical | [integrity-failures.md](runbooks/integrity-failures.md) |
| Auto-run Success Rate | <90% | Warning | [auto-run-failures.md](runbooks/auto-run-failures.md) |
| Data Ingestion Lag | >2 days | Critical | [ingestion-failures.md](runbooks/ingestion-failures.md) |
| Remediation Activity | >10/7d | Warning | [remediation-activity.md](runbooks/remediation-activity.md) |

## Troubleshooting

### Common Issues

1. **Workflow not running**
   - Check GitHub Actions status
   - Verify cron schedule syntax
   - Ensure workflow is enabled

2. **Alerts not being sent**
   - Verify SLACK_WEBHOOK_URL secret is set
   - Check dry_run parameter
   - Review alert history in logs

3. **Integrity failures**
   - Follow [integrity-failures.md](runbooks/integrity-failures.md) runbook
   - Check recent code changes
   - Verify data source quality

4. **File not found errors**
   - Workflow now uses consistent file resolution
   - Creates test data automatically if needed
   - Check dashboard/data directory exists

## Manual Execution

To run the daily operations manually:

```bash
# Via GitHub CLI
gh workflow run "Daily Operations"

# With dry-run mode
gh workflow run "Daily Operations" -f dry_run=true

# Via GitHub UI
Navigate to Actions → Daily Operations → Run workflow
```

## Success Criteria

The daily operations are considered successful when:
- ✅ Integrity failure rate <1%
- ✅ Auto-run success rate ≥90%
- ✅ No critical alerts triggered
- ✅ All steps complete without errors

---

**Last Updated**: 2025-08-13
**Version**: 1.1.0 (with consistent file resolution)