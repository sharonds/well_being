# Phase 5 – Issue Doc: Plan Engine and Phase A Delivery

Owner: @sharonds
Status: Proposed
Date: 2025-08-13

## Goals
- Deliver Phase A of user stories quickly and safely: a single “Today” plan with Tier-1 chips and minimal feedback loop.
- Establish a deterministic PlanEngine with guardrails, persistence, and observability.

## Scope (Phase A only)
- Deterministic plan generation at morning run.
- Minimal UI behaviors: Plan card, Tier-1 chips, Done/Snooze, energy rating modal.
- Persistence for plan and adherence; idempotent per local day.
- Lightweight observability counters and existing ops integration.

## Out of scope (later phases)
- Start timer/logging, Focus screen, Meditation nudge confidence model, Settings UI expansion.

## Deliverables
1) Module: PlanEngine
- Inputs (preferred, all optional except band/score): band, score, delta, rhr_delta_7d, sleep_hours, sleep_var_14d, stress_midday|daily, steps_trend_7d, hrv_delta?, sugar_flag?
- Output: {plan_type: easy|maintain|hard, minutes_range, addons: [core|breath|nsdr|walk?], why: [top1–2 deltas], triggers: [coach?]}
- Guards: if anomaly → never hard. Missing metrics → conservative Easy + reason.

2) Persistence
- Files: plan_daily.jsonl, adherence_daily.jsonl (JSON Lines; atomic writes + backups)
- Keys: date (local YYYY-MM-DD), created_at, schema_version
- Idempotence: one plan per day unless explicit recompute flag

3) Morning job
- Window: 07:00 local ± configurable; DST-aware
- Behavior: generate plan if none exists; skip otherwise; log

4) UI wiring (minimal)
- Plan card: single line using copy kit
- Tier-1 chips: checkable toggles
- Buttons: Done, Snooze
- Energy modal: 1–10 quick input (phase A minimal)

5) Config + feature flags
- dashboard/config.py additions: thresholds (anomaly, sleep variance), windows (trend), flags (ENABLE_PLAN_ENGINE, ENABLE_INSIGHT_CARD, ENABLE_COACH_CHIP)

6) Observability
- Counters appended to ops metrics: plan_generated, plan_skipped_missing_data, adherence_logged

7) Privacy
- Extend privacy scan to include new files; ensure no raw metrics are exported (only deltas/flags)

## Thresholds (defaults)
- Anomaly if any:
  - rhr_delta_7d ≥ +7 bpm OR sleep_hours < 6.5h OR stress_high OR (sugar_flag AND hrv_delta < 0)
- Sleep variance coach: 14d avg > 60m; target ±30m
- Steps trend down: 7d slope negative and below baseline

## Tests
- Unit tests for PlanEngine boundaries: anomaly precedence, rhrΔ=+7, sleep=6.5h, band consistency (no hard on anomaly), missing metrics fallback.
- Persistence tests: idempotent write, recompute flag behavior, timezone/DST basic guard.

## Tasks
- [ ] Add PlanEngine module and tests
- [ ] Add persistence (plan_daily.jsonl, adherence_daily.jsonl) using atomic utilities
- [ ] Morning job wiring with existing scheduler
- [ ] UI: render Plan card, chips, Done/Snooze, energy modal
- [ ] Update dashboard/config.py with thresholds and flags
- [ ] Extend metrics exporter counters
- [ ] Update privacy scan to include new files
- [ ] Docs: README (Phase A usage), update CHANGELOG

## Acceptance criteria
- Plan emits ≤3 actions, renders <300ms from cached data
- Never emits hard plan on anomaly days
- One plan per local day; recompute requires explicit flag
- Privacy scan green, ops workflows continue to pass

## References
- PHASE_5_USER_STORIES_REVIEW.md
- docs/PRD.md (Section 7.2 formulas)
- .github/workflows/daily-ops.yml
- phase_3_2_issue.md, phase_3_3_issue.md, phase_4_issue.md
