# 📊 Phase 3: Operational Reliability & Trust

## Executive Summary
Based on ChatGPT-5 review, Phase 3 focuses on operational reliability and user trust without expanding metrics or analytics. Pure hardening and observability.

## 🎯 Acceptance Criteria

| ID | Criteria | Priority | Effort |
|----|----------|----------|--------|
| AC1 | Auto-refresh 14-day success rate ≥90% | HIGH | S |
| AC2 | Zero duplicate scores for single date (idempotence) | HIGH | S |
| AC3 | Integrity failures <1% over 14 days | HIGH | S |
| AC4 | Battery skip logic triggers correctly | MEDIUM | S |
| AC5 | Hash & schema drift detection gates merges | HIGH | M |
| AC6 | Telemetry privacy test baseline green | HIGH | S |
| AC7 | Completeness delta alerting (7d vs 30d) | MEDIUM | M |
| AC8 | Recovery path for corrupted history | MEDIUM | M |

## 🔧 Implementation Tasks

### 1. Idempotence & Duplicate Prevention (AC2)
```python
# Add to fetch_garmin_data.py
def check_duplicate(date: str, schema_version: str) -> bool:
    """Prevent duplicate insertions for same date."""
    # Check existing records
    # Return True if duplicate exists
```

### 2. Auto-Refresh KPI Monitoring (AC1)
```python
# Add to garmin_integrity.py
def calculate_success_rate(telemetry_records: list, days: int = 14) -> float:
    """Calculate auto-refresh success rate."""
    # Count auto_run=1 vs expected days
    # Return percentage
```

### 3. Battery-Aware Safe Mode (AC4)
```python
# Add to fetch script
def should_skip_battery(battery_level: int, threshold: int = 15) -> bool:
    """Skip fetch if battery low."""
    if battery_level < threshold:
        logger.info(f"SKIP_BATTERY: {battery_level}% < {threshold}%")
        return True
    return False
```

### 4. Enhanced Drift Detection (AC5)

#### Formula Hash Change Workflow
```python
# scripts/check_drift.py
def validate_formula_change(commit_message: str, old_hash: str, new_hash: str) -> bool:
    """Validate legitimate formula changes."""
    if "[FORMULA-INTENT]" in commit_message:
        # Log the change
        with open("parity_update.json", "w") as f:
            json.dump({
                "old_hash": old_hash,
                "new_hash": new_hash,
                "reason": commit_message,
                "timestamp": datetime.now().isoformat()
            }, f)
        return True
    return False
```

### 5. Privacy Guard Test (AC6)
```python
# tests/test_privacy_redaction.py
def test_no_raw_metrics_in_telemetry():
    """Red-team test to ensure no raw values leak."""
    # Try to inject raw values
    malicious_record = {
        "steps_raw": 12345,  # Should be rejected
        "actual_hr": 65,     # Should be rejected
    }
    # Assert pipeline strips or rejects
```

### 6. Completeness Delta Monitoring (AC7)
```python
def check_completeness_regression(records_7d: list, records_30d: list) -> dict:
    """Alert if recent completeness drops."""
    avg_7d = calculate_avg_completeness(records_7d)
    avg_30d = calculate_avg_completeness(records_30d)
    
    if avg_7d < avg_30d * 0.8:  # 20% drop threshold
        return {"alert": True, "7d": avg_7d, "30d": avg_30d}
```

### 7. Self-Healing Persistence (AC8)
```python
def recover_corrupted_history(history_file: str) -> bool:
    """Quarantine and rebuild corrupted history."""
    try:
        validate_history(history_file)
    except CorruptionError:
        # Quarantine
        shutil.move(history_file, f"{history_file}.corrupted")
        # Rebuild from telemetry
        rebuild_from_telemetry()
        logger.info("RECOVERED_HISTORY: Rebuilt from telemetry")
        return True
```

## 📁 New Artifacts

### telemetry_schema.json
```json
{
  "version": "2.0.0",
  "fields": {
    "date": "string",
    "timestamp_utc": "string",
    "schema_version": "string",
    "auto_run": "integer",
    "steps_present": "integer",
    "rhr_present": "integer",
    "sleep_present": "integer",
    "stress_present": "integer",
    "metrics_mask": "integer",
    "score": "integer",
    "band": "string",
    "completeness_pct": "float"
  },
  "hash": "SHA256"
}
```

### Enhanced CI Guard
```yaml
# .github/workflows/phase-guard.yml additions
- name: Check KPIs
  run: |
    SUCCESS_RATE=$(python scripts/calculate_kpi.py --metric success_rate)
    if [ "$SUCCESS_RATE" -lt "90" ]; then
      echo "⚠️ Auto-refresh success rate below 90%: $SUCCESS_RATE%"
      exit 1
    fi
    
- name: Check Completeness Delta
  run: |
    python scripts/check_completeness_delta.py --threshold 20
    
- name: Verify No Duplicates
  run: |
    python scripts/check_duplicates.py --days 14
```

## 🚫 Explicitly Deferred (Scope Discipline)

- ❌ HRV or new physiological metrics
- ❌ Long-term trend analytics (beyond 30d)
- ❌ Alerting/notification system
- ❌ Cloud sync or multi-user
- ❌ Predictive/ML layers
- ❌ Calorie tracking
- ❌ VO2 max

## 📈 Success Metrics

### Primary KPIs
- Auto-refresh success rate: ≥90% over 14 days
- Data integrity failures: <1% 
- Zero duplicate entries
- Privacy tests: 100% pass

### Secondary KPIs
- Completeness average: >70%
- Battery skip events: <5% of attempts
- Recovery events: <1 per week
- Formula drift: 0 unintentional changes

## 🗓️ Execution Order

### Week 1: Core Protection
1. Idempotence & duplicate prevention
2. Privacy redaction tests
3. Enhanced drift detection

### Week 2: Operational Safety
4. Auto-refresh KPI monitoring
5. Battery skip logic
6. Completeness delta alerting

### Week 3: Recovery & Hardening
7. Self-healing persistence
8. Ingestion quality gates
9. Final validation suite

## 🧪 Test Coverage Additions

```python
# New test cases needed
- test_no_duplicates_same_date()
- test_battery_skip_at_threshold()
- test_formula_change_with_intent_tag()
- test_formula_change_without_intent_fails()
- test_privacy_no_raw_metrics()
- test_completeness_delta_alert()
- test_corrupted_history_recovery()
- test_schema_version_mismatch()
- test_mask_bit_ordering()
- test_telemetry_compression()
```

## 📊 Monitoring Dashboard Additions

### New Panels Needed
1. **Auto-Refresh Success Rate** (14-day rolling)
2. **Completeness Trend** (7d vs 30d comparison)
3. **Integrity Failures** (daily count)
4. **Battery Skip Events** (daily count)
5. **Duplicate Detection** (alert panel)

## 🔒 Privacy Enhancements

### Telemetry Compression
Single line per day: `{date, score, band, mask, auto, fail_count}`

### Raw Value Protection
- Regex scan for integers >10000
- Decimal pattern detection
- Automatic stripping of non-schema fields

## 📋 Pre-Phase 3 Checklist

- [ ] Test Garmin connection with real account
- [ ] Verify Phase 2 telemetry working
- [ ] Baseline current KPIs
- [ ] Create test data for edge cases
- [ ] Review and approve AC priorities

## 🎯 Definition of Done

Phase 3 is complete when:
1. All 8 ACs are green
2. 14 consecutive days without privacy violations
3. 14 consecutive days without drift violations
4. KPIs meet thresholds for 14 days
5. All new tests passing in CI

---

**Estimated Duration**: 3 weeks
**Risk Level**: Low (pure hardening, no new features)
**Dependencies**: Phase 2 must be validated with real data first