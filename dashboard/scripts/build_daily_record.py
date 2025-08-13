#!/usr/bin/env python3
"""Build a single daily record JSON object from raw metric inputs.
Does NOT fetch from Garmin; acts as a transformation layer used by export script.
"""
from __future__ import annotations
from typing import Optional, Dict, Any
import time
from dashboard.score.engine import compute_score, MetricInputs, ScoreFlags

FORMULA_VERSION = "1.0.0"  # align with .env.example


def build_daily_record(
    date: str,
    steps: Optional[int],
    rhr: Optional[int],
    sleep_h: Optional[float] = None,
    stress: Optional[int] = None,
    enable_sleep: bool = False,
    enable_stress: bool = False,
    tz_offset_min: int = 0,
    run_mode: str = "batch",
) -> Dict[str, Any]:
    flags = ScoreFlags(enable_sleep=enable_sleep, enable_stress=enable_stress)
    result = compute_score(
        MetricInputs(steps=steps, rhr=rhr, sleep_hours=sleep_h, stress=stress),
        flags,
    )
    record = {
        "date": date,
        "compute_ts_utc": int(time.time() * 1000),
        "score": result.score,
        "band": result.band,
        "metrics_raw": {
            "steps": steps,
            "rhr": rhr,
            "sleep_h": sleep_h,
            "stress": stress,
        },
        "metrics_norm": result.normalized,
        "weights_active": result.weights,
        "contrib": result.contributions,
        "missing": result.missing,
        "flags": {
            "sleep": enable_sleep,
            "stress": enable_stress,
            "hrv": False,
        },
        "formula_version": FORMULA_VERSION,
        "run_mode": run_mode,
        "error_codes": [],
        "tz_offset_min": tz_offset_min,
    }
    return record

if __name__ == "__main__":
    # Simple smoke example
    import json
    rec = build_daily_record("2025-08-12", 10000, 50, sleep_h=7, stress=40, enable_sleep=True, enable_stress=True)
    print(json.dumps(rec, indent=2))
