"""Well-Being Score Engine (Python parity)"""
from __future__ import annotations
from dataclasses import dataclass
from math import floor
from typing import Optional, Dict, Any

BASE_WEIGHTS = {
	"steps": 0.40,
	"rhr": 0.30,
	"sleep": 0.20,
	"stress": 0.10,
}

@dataclass
class ScoreFlags:
	enable_sleep: bool = False
	enable_stress: bool = False
	enable_hrv: bool = False  # placeholder

@dataclass
class MetricInputs:
	steps: Optional[int]
	rhr: Optional[int]
	sleep_hours: Optional[float] = None
	stress: Optional[int] = None
	hrv: Optional[int] = None

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
	return (80 - _clamp(rhr, 40, 80)) / 40.0

def normalize_sleep(hours: Optional[float]) -> Optional[float]:
	if hours is None:
		return None
	return min(hours, 8.0) / 8.0

def normalize_stress_inverse(stress: Optional[int]) -> Optional[float]:
	if stress is None:
		return None
	return (100 - _clamp(stress, 0, 100)) / 100.0

def redistribute_weights(flags: ScoreFlags, inputs: MetricInputs) -> Dict[str, float]:
	active: Dict[str, float] = {}
	if inputs.steps is not None:
		active["steps"] = BASE_WEIGHTS["steps"]
	if inputs.rhr is not None:
		active["rhr"] = BASE_WEIGHTS["rhr"]
	if flags.enable_sleep and inputs.sleep_hours is not None:
		active["sleep"] = BASE_WEIGHTS["sleep"]
	if flags.enable_stress and inputs.stress is not None:
		active["stress"] = BASE_WEIGHTS["stress"]
	total = sum(active.values())
	return {k: v / total for k, v in active.items()} if total else {}

def compute_score(inputs: MetricInputs, flags: ScoreFlags | None = None) -> ScoreResult:
	flags = flags or ScoreFlags()
	weights = redistribute_weights(flags, inputs)
	norm = {
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
	score_int = _round_score(score_acc * 100.0)
	band = next((nm for lo, hi, nm in BAND_MAP if lo <= score_int <= hi), "Unknown")
	missing = []
	if inputs.steps is None:
		missing.append("steps")
	if inputs.rhr is None:
		missing.append("rhr")
	if flags.enable_sleep and inputs.sleep_hours is None:
		missing.append("sleep")
	if flags.enable_stress and inputs.stress is None:
		missing.append("stress")
	return ScoreResult(score_int, band, contributions, weights, {k: v for k, v in norm.items() if v is not None}, missing)

if __name__ == "__main__":  # quick smoke
	print(compute_score(MetricInputs(8000, 55)))
