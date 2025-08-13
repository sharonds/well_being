"""Parity tests for well-being score engine.
Run manually for now (no test framework dependency yet).
"""
from dashboard.score.engine import compute_score, MetricInputs, ScoreFlags


def assert_equal(label, got, expected):
    if got != expected:
        raise AssertionError(f"{label}: got {got} expected {expected}")


def test_examples():
    # Example A
    rA = compute_score(MetricInputs(steps=8000, rhr=55))
    assert_equal("Example A", rA.score, 65)

    # Example B (flags)
    rB = compute_score(MetricInputs(steps=12500, rhr=48, sleep_hours=7, stress=35), ScoreFlags(enable_sleep=True, enable_stress=True))
    assert_equal("Example B", rB.score, 88)

    # Example C
    rC = compute_score(MetricInputs(steps=3000, rhr=70))
    assert_equal("Example C", rC.score, 25)

    print("All vector tests passed.")

if __name__ == "__main__":
    test_examples()
