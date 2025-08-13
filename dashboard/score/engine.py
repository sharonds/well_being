"""Well-Being Score Engine (Python Port)
Parity-focused implementation mirroring wearable Monkey C logic.

Phases / Features:
- Supports steps & resting HR baseline.
- Optional flags: sleep, stress, hrv (future expansion; wired but default False).
- Weight redistribution when metrics absent.
- Rounding: floor(x + 0.5)

Author: (auto-generated scaffold)
"""
from __future__ import annotations
from dataclasses import dataclass
from math import floor
from typing import Optional, Dict, Any

# Base weights when all (no HRV) present (sleep, stress optional flags)
BASE_WEIGHTS = {
    "steps": 0.40,
    "rhr": 0.30,
    "sleep": 0.20,
    "stress": 0.10,
    # HRV weight TBD (feature flagged, not active yet)
}

@dataclass
class ScoreFlags:
    enable_sleep: bool = False
    enable_stress: bool = False
    enable_hrv: bool = False  # placeholder for future

@dataclass
class MetricInputs:
    steps: Optional[int]
    rhr: Optional[int]
    sleep_hours: Optional[float] = None  # hours
    stress: Optional[int] = None         # 0-100 scale
    hrv: Optional[int] = None            # ms or normalized external (not used yet)

@dataclass
class ScoreResult:
    score: int
    band: str
    contributions: Dict[str, float]
    weights: Dict[str, float]
    normalized: Dict[str, float]
    missing: list[str]

BAND_MAP = [
    (0, 39, "Take it easy"),
    (40, 69, "Maintain"),
    (70, 100, "Go for it"),
]


def _round_score(value: float) -> int:
    return int(floor(value + 0.5))


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def normalize_steps(steps: Optional[int]) -> Optional[float]:
    if steps is None:
        return None
    return min(steps, 12000) / 12000.0


def normalize_rhr_inverse(rhr: Optional[int]) -> Optional[float]:
    if rhr is None:
        return None
    # clamp to [40, 80]; 40 best -> 1.0, 80 worst -> 0.0
    return (80 - _clamp(rhr, 40, 80)) / 40.0


def normalize_sleep(hours: Optional[float]) -> Optional[float]:
    if hours is None:
        return None
    # simple linear target 8h cap
    return min(hours, 8.0) / 8.0


def normalize_stress_inverse(stress: Optional[int]) -> Optional[float]:
    if stress is None:
        return None
    # invert 0 best 100 worst -> 1..0
    return (100 - _clamp(stress, 0, 100)) / 100.0


def redistribute_weights(flags: ScoreFlags, inputs: MetricInputs) -> Dict[str, float]:
    active = {}
    if inputs.steps is not None:
        active["steps"] = BASE_WEIGHTS["steps"]
    if inputs.rhr is not None:
        active["rhr"] = BASE_WEIGHTS["rhr"]
    if flags.enable_sleep and inputs.sleep_hours is not None:
        active["sleep"] = BASE_WEIGHTS["sleep"]
    if flags.enable_stress and inputs.stress is not None:
        active["stress"] = BASE_WEIGHTS["stress"]
    # HRV omitted for now
    total = sum(active.values())
    if total == 0:
        return {}
    return {k: v / total for k, v in active.items()}


def compute_score(inputs: MetricInputs, flags: ScoreFlags | None = None) -> ScoreResult:
    flags = flags or ScoreFlags()

    weights = redistribute_weights(flags, inputs)

    norm: Dict[str, Optional[float]] = {
        "steps": normalize_steps(inputs.steps),
        "rhr_inv": normalize_rhr_inverse(inputs.rhr),
        "sleep": normalize_sleep(inputs.sleep_hours) if flags.enable_sleep else None,
        "stress_inv": normalize_stress_inverse(inputs.stress) if flags.enable_stress else None,
    }

    score_acc = 0.0
    contributions: Dict[str, float] = {}
    for key, w in weights.items():
        if key == "steps":
            val = norm["steps"]
        elif key == "rhr":
            val = norm["rhr_inv"]
        elif key == "sleep":
            val = norm["sleep"]
        elif key == "stress":
            val = norm["stress_inv"]
        else:
            val = None
        if val is None:
            continue
        contributions[key] = w * val
        score_acc += contributions[key]

    score_raw = score_acc * 100.0
    score_int = _round_score(score_raw)

    band = "Unknown"
    for lo, hi, name in BAND_MAP:
        if lo <= score_int <= hi:
            band = name
            break

    missing = []
    if inputs.steps is None: missing.append("steps")
    if inputs.rhr is None: missing.append("rhr")
    if flags.enable_sleep and inputs.sleep_hours is None: missing.append("sleep")
    if flags.enable_stress and inputs.stress is None: missing.append("stress")

    return ScoreResult(
        score=score_int,
        band=band,
        contributions=contributions,
        weights=weights,
        normalized={k: v for k, v in norm.items() if v is not None},
        missing=missing,
    )


def compute_examples() -> Dict[str, Any]:
    """Utility: returns computed scores for documented examples A, B, C.
    Example definitions (from PRD test vectors):
    A: steps=8000, rhr=55 -> expected 65 (Phase1 baseline)
    B: steps=12500 (cap 12000), rhr=48, sleep=7h, stress=35 -> expected 88 (with flags)
    C: steps=3000, rhr=70 -> expected 25
    """
    ex = {}
    # Example A
    ex["A"] = compute_score(MetricInputs(steps=8000, rhr=55), ScoreFlags())
    # Example B (enable flags)
    ex["B"] = compute_score(MetricInputs(steps=12500, rhr=48, sleep_hours=7, stress=35), ScoreFlags(enable_sleep=True, enable_stress=True))
    # Example C
    ex["C"] = compute_score(MetricInputs(steps=3000, rhr=70), ScoreFlags())
    return {k: v.score for k, v in ex.items()}

if __name__ == "__main__":  # simple manual smoke
    print(compute_examples())
