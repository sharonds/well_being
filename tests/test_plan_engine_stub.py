"""
Stub tests for upcoming PlanEngine. Replace with real tests in Phase 5.

Contract sketch:
- Inputs: band, score, rhr_delta_7d, sleep_hours, sleep_var_14d, stress, steps_trend_7d, hrv_delta?, sugar_flag?
- Guarantees: never 'hard' on anomaly; conservative fallback on missing metrics.
"""


def test_anomaly_prevents_hard():
    # Given anomaly conditions, engine must never emit 'hard'
    # Placeholder assertion until PlanEngine is implemented
    assert True


def test_sleep_boundary():
    # sleep = 6.5h boundary should classify per spec
    assert True


def test_rhr_boundary():
    # rhrΔ=+7 boundary should trigger anomaly branch
    assert True


def test_missing_metrics_conservative():
    # Missing optional signals falls back to conservative Easy
    assert True
