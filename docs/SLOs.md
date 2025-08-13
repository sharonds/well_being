# Service Level Objectives (SLOs)

## Overview

This document defines the Service Level Objectives for the Wellness Dashboard production system.

## SLO Definitions

### 1. Data Integrity
**Objective**: Maintain data integrity with minimal corruption or inconsistencies

| Metric | Target | Measurement Window | Alert Threshold |
|--------|--------|-------------------|-----------------|
| Integrity Failure Rate | < 1% | 14 days rolling | ≥ 1% |
| Band Mapping Accuracy | 100% | Per record | Any mismatch |
| Schema Validation Pass Rate | > 99% | 24 hours | < 99% |

### 2. Automation Reliability
**Objective**: Ensure automated processes run successfully

| Metric | Target | Measurement Window | Alert Threshold |
|--------|--------|-------------------|-----------------|
| Auto-run Success Rate | ≥ 90% | 14 days rolling | < 90% |
| Daily Job Completion | 100% | 24 hours | Any failure |
| Remediation Success Rate | > 95% | 7 days | < 95% |

### 3. Data Freshness
**Objective**: Keep data current and up-to-date

| Metric | Target | Measurement Window | Alert Threshold |
|--------|--------|-------------------|-----------------|
| Data Ingestion Lag | ≤ 1 day | Current | > 2 days |
| Metrics Export Freshness | < 5 minutes | Per export | > 10 minutes |
| Alert Delivery Time | < 2 minutes | Per alert | > 5 minutes |

### 4. System Availability
**Objective**: Maintain system availability and responsiveness

| Metric | Target | Measurement Window | Alert Threshold |
|--------|--------|-------------------|-----------------|
| CI/CD Pipeline Success | > 95% | 7 days | < 90% |
| Garmin API Success Rate | > 98% | 24 hours | < 95% |
| Dashboard Availability | > 99% | 30 days | < 98% |

## SLO Monitoring

### Daily Checks
- Integrity failure rate (automated via daily-ops workflow)
- Auto-run success rate (automated via daily-ops workflow)
- Data ingestion status (automated via alerts.py)

### Weekly Reviews
- Remediation activity trends
- Alert response times
- False positive rate

### Monthly Reviews
- Overall SLO compliance
- Trend analysis
- Capacity planning

## Ownership & Escalation

### Primary Owner
- **Role**: Platform Engineering
- **Contact**: Via GitHub Issues
- **Response Time**: < 4 hours for critical alerts

### Escalation Path
1. **Level 1**: Automated remediation (immediate)
2. **Level 2**: On-call engineer (< 1 hour)
3. **Level 3**: Platform lead (< 4 hours)
4. **Level 4**: Engineering manager (< 24 hours)

## Alert Channels

### Critical Alerts (Immediate Action Required)
- Integrity failure rate ≥ 1%
- Data ingestion > 7 days behind
- Multiple remediation failures

**Channel**: Slack #wellness-alerts (webhook configured)

### Warning Alerts (Action Within 24 Hours)
- Auto-run success < target
- High remediation activity
- CI/CD failures

**Channel**: Daily ops report + GitHub Issues

### Informational (No Action Required)
- Daily metrics summary
- Burn-in progress updates
- Retention policy executions

**Channel**: GitHub Actions summary

## SLO Review Process

### Quarterly Review
- Analyze SLO achievement rates
- Adjust thresholds based on historical data
- Update runbooks based on incidents

### Annual Planning
- Review architecture for SLO improvements
- Plan capacity for growth
- Update monitoring infrastructure

## Burn-in Period SLOs

During the 30-day burn-in period, the following adjusted SLOs apply:

| Metric | Burn-in Target | Notes |
|--------|---------------|-------|
| Integrity Failure Rate | < 1% | Same as production |
| Auto-run Success Rate | ≥ 80% | Slightly relaxed |
| Zero Critical Incidents | 30 days | No unresolved critical issues |
| Alert False Positive Rate | < 20% | Tuning period |

## Success Criteria for GA Release

The system meets GA release criteria when:
- ✅ 30-day burn-in completed
- ✅ All P1 SLOs met for 14 consecutive days
- ✅ No unresolved critical incidents
- ✅ Runbooks validated through real incidents
- ✅ Alert channels tested and verified

---

*Last Updated: 2025-08-13*
*Next Review: End of burn-in period*