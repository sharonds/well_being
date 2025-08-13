# Release Checklist for GA

## Pre-Release Requirements

### ✅ Code Quality
- [ ] All tests passing (33+ tests)
- [ ] No critical security vulnerabilities
- [ ] Code coverage > 80%
- [ ] No hardcoded secrets or credentials
- [ ] All TODOs addressed or documented

### ✅ Operational Readiness
- [ ] 30-day burn-in period completed
- [ ] Integrity failure rate < 1% for 14 consecutive days
- [ ] Auto-run success rate ≥ 90% for 14 consecutive days
- [ ] No unresolved critical incidents
- [ ] All P1 bugs fixed

### ✅ Monitoring & Alerting
- [ ] Metrics exporter operational
- [ ] Alert channels configured and tested
- [ ] SLOs defined and published
- [ ] Runbooks created and validated
- [ ] Daily ops workflow running successfully

### ✅ Documentation
- [ ] README up to date
- [ ] CHANGELOG current
- [ ] API documentation complete
- [ ] Runbooks cover all alert types
- [ ] Installation guide verified

### ✅ CI/CD Pipeline
- [ ] Quality gates active and enforcing
- [ ] Privacy scan blocking bad commits
- [ ] Integrity check in CI
- [ ] Automated tests running on every PR
- [ ] Release automation configured

### ✅ Data Management
- [ ] Retention policy active
- [ ] Backup strategy documented
- [ ] Recovery procedures tested
- [ ] Data migration path clear
- [ ] Privacy compliance verified

### ✅ Security
- [ ] Secrets management configured
- [ ] Access controls defined
- [ ] Audit logging enabled
- [ ] Vulnerability scan passed
- [ ] Security review completed

## Release Process

### 1. Pre-Release Validation (T-7 days)
```bash
# Run comprehensive validation
./scripts/validate_release.sh

# Check all SLOs
python3 dashboard/scripts/ops/metrics_exporter.py --format json | \
  jq '.integrity.failure_rate_14d_pct, .auto_run.success_rate_pct'

# Verify no critical alerts
python3 dashboard/scripts/ops/alerts.py --dry-run
```

### 2. Release Candidate (T-3 days)
```bash
# Tag release candidate
git tag -a v3.4.0-rc1 -m "Release candidate 1"
git push origin v3.4.0-rc1

# Deploy to staging
gh workflow run "Release Automation" -f version=v3.4.0-rc1 -f environment=staging
```

### 3. Final Validation (T-1 day)
- [ ] Staging deployment successful
- [ ] Smoke tests passed
- [ ] Performance benchmarks met
- [ ] No new critical issues

### 4. Release (T-0)
```bash
# Create release tag
git tag -a v3.4.0 -m "GA Release - Production Ready"
git push origin v3.4.0

# Create GitHub release
gh release create v3.4.0 \
  --title "v3.4.0 - GA Release" \
  --notes-file RELEASE_NOTES.md \
  --verify-tag
```

### 5. Post-Release (T+1 day)
- [ ] Monitor metrics closely for 24 hours
- [ ] Verify all alerts functioning
- [ ] Check user feedback channels
- [ ] Update status page

## Sign-off Requirements

### Technical Sign-off
- [ ] **Platform Lead**: Architecture and implementation approved
- [ ] **QA Lead**: Testing complete and passed
- [ ] **Security**: Security review passed

### Business Sign-off  
- [ ] **Product Owner**: Features meet requirements
- [ ] **Operations**: Runbooks and on-call ready

### Final Approval
- [ ] **Engineering Manager**: Overall release approved
- [ ] **Release Date**: _______________
- [ ] **Released By**: _______________

## Rollback Plan

If critical issues discovered post-release:

1. **Immediate Actions**
   ```bash
   # Revert to previous version
   git revert <release-commit>
   git tag -a v3.4.1-hotfix -m "Emergency rollback"
   git push origin v3.4.1-hotfix
   ```

2. **Communication**
   - Post in #wellness-alerts
   - Update status page
   - Create incident report

3. **Root Cause Analysis**
   - Complete within 48 hours
   - Update runbooks
   - Add regression tests

## Success Criteria

The release is considered successful when:
- ✅ 48 hours post-release with no critical issues
- ✅ All SLOs maintained
- ✅ No emergency rollbacks required
- ✅ User feedback positive or neutral

## Appendix: Validation Scripts

### Comprehensive Validation
```bash
#!/bin/bash
# validate_release.sh

echo "🔍 Running release validation..."

# Run all tests
python3 -m pytest dashboard/tests/ -v

# Check integrity
python3 dashboard/scripts/phase3/integrity_monitor.py dashboard/data/*.jsonl

# Verify CI gates
gh workflow run "Quality Gates"

# Check metrics
python3 dashboard/scripts/ops/metrics_exporter.py --format json

echo "✅ Validation complete"
```

### Smoke Test
```bash
#!/bin/bash
# smoke_test.sh

# Test metric export
curl -f http://localhost:8080/metrics || exit 1

# Test alert system
python3 dashboard/scripts/ops/alerts.py --test || exit 1

# Test data pipeline
python3 dashboard/scripts/fetch_garmin_data.py --date $(date -I) --dry-run || exit 1

echo "✅ Smoke tests passed"
```

---

**Document Version**: 1.0.0
**Last Updated**: 2025-08-13
**Next Review**: Before GA release