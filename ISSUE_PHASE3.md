# Phase 3: Operational Reliability Implementation

## Objective
Transform the wellness tracker from manual to autonomous operation with 90%+ reliability.

## Acceptance Criteria Checklist

### Ready to Implement
- [ ] **AC1**: Add auto_run flag to telemetry records
  - Add field to fetch_garmin_data.py
  - Track in telemetry (1 for auto, 0 for manual)
  - Create KPI panel showing 14-day success rate

- [ ] **AC5**: Formula drift detection with [FORMULA-CHANGE] gating
  - Calculate and store formula hash
  - Block changes without [FORMULA-CHANGE] in commit message
  - Add CI validation step

- [ ] **AC4**: Battery safeguard implementation
  - Add battery check before fetch
  - Skip when <15% with SKIP_BATTERY log
  - Add test for threshold behavior

- [ ] **AC7**: Completeness delta monitoring
  - Compare 7-day vs 30-day averages
  - Alert if 7-day drops >15% below 30-day
  - Add to dashboard

- [ ] **AC3**: Data integrity monitoring
  - Track failures per day
  - Ensure <1% failure rate over 14 days
  - Add integrity panel to dashboard

- [ ] **AC8**: Self-healing persistence
  - Detect corrupted history files
  - Quarantine and rebuild from telemetry
  - Log RECOVERED_HISTORY events

### Already Complete
- [x] **AC2**: Idempotence & duplicate prevention ✅
- [x] **AC6**: Privacy guard tests ✅

## Implementation Order
1. AC1 - Auto_run flag (simplest, enables KPI tracking)
2. AC5 - Formula drift (protects consistency)
3. AC4 - Battery safeguard (user experience)
4. AC7 - Completeness monitoring (data quality)
5. AC3 & AC8 - Advanced reliability features

## Files to Modify
- `dashboard/scripts/fetch_garmin_data.py` - Add auto_run, battery check
- `dashboard/scripts/formula_hash.py` - New file for drift detection
- `.github/workflows/phase-guard.yml` - Add formula hash validation
- `dashboard/scripts/completeness_monitor.py` - New file for AC7
- `dashboard/tests/test_phase3_*.py` - Test files for each AC

## Success Metrics
- 90%+ auto-refresh success rate over 14 days
- 0 duplicate entries
- <1% data integrity failures
- 100% privacy test pass rate

## Test Requirements
Each AC must include:
- Unit tests for new functions
- Integration test with existing pipeline
- 14-day stability validation

## Notes
- Maintain backward compatibility
- No new metrics or analytics (scope discipline)
- Focus on reliability, not features

---
Label: `enhancement`, `phase-3`, `automation-ready`
Assignee: @sharonds