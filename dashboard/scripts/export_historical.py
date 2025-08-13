#!/usr/bin/env python3
"""Historical export script (placeholder data source).
Future: replace placeholder with real Garmin fetch calls.
Generates JSON Lines file of daily records using build_daily_record.

Usage:
  PYTHONPATH=. python3 dashboard/scripts/export_historical.py output.jsonl
"""
from __future__ import annotations
import sys, json, pathlib, random, datetime
from typing import Iterable
from dashboard.scripts.build_daily_record import build_daily_record

# Placeholder synthetic generator (30 days)

def _date_seq(days: int) -> Iterable[str]:
    today = datetime.date.today()
    for i in range(days):
        d = today - datetime.timedelta(days=(days - 1 - i))
        yield d.isoformat()


def main():
    if len(sys.argv) != 2:
        print("Usage: export_historical.py <output.jsonl>", file=sys.stderr)
        return 1
    out_path = pathlib.Path(sys.argv[1])
    days = 30

    with out_path.open("w", encoding="utf-8") as f:
        for date in _date_seq(days):
            # Synthetic metrics with some variation
            steps = random.randint(3000, 13000)
            rhr = random.randint(45, 70)
            sleep_h = round(random.uniform(5.0, 8.0), 1)
            stress = random.randint(25, 60)
            rec = build_daily_record(
                date,
                steps,
                rhr,
                sleep_h=sleep_h,
                stress=stress,
                enable_sleep=True,
                enable_stress=True,
                tz_offset_min=-420,
                run_mode="historical_synth",
            )
            f.write(json.dumps(rec) + "\n")

    print(f"Exported {days} synthetic days -> {out_path}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
