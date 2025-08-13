# Phase 5 – Issue Doc: Plan Engine and Phase A Delivery

Owner: @sharonds
Status: Proposed
Date: 2025-08-13

## Goals
- Deliver Phase 5A with local compute and simple sharing: a single “Today” plan with minimal feedback.
- Establish PlanEngine with guardrails/persistence and expose insights to a web app via QR/paste (no MFA, no companion app).

## Scope (Phase A only)
- Deterministic plan generation at morning run.
- Minimal UI behaviors: Plan card, Tier-1 chips, Done/Snooze, energy rating modal.
- Persistence for plan and adherence; idempotent per local day.
- Lightweight observability counters and existing ops integration.

## Out of scope (later phases)
- Start timer/logging, Focus screen, Meditation nudge confidence model, Settings UI expansion.
- iOS companion app, server ingestion, Garmin Health API.

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

4) UI wiring (minimal on-device)
- Plan card: single line using copy kit
- Tier-1 chips: checkable toggles
- Buttons: Done, Snooze
- Energy modal: 1–10 quick input (phase A minimal)

5) Web sharing (QR + paste, zero-backend)
- Watch: render QR for insight_packet_v1; fallback to copy/paste JSON
- Web app stub: Import page with “Scan QR” and “Paste JSON”
- Storage: IndexedDB helper with idempotent upsert by (date,type)
- JSON Schema: validate envelope + payload; version-gated parsing

6) Config + feature flags
- dashboard/config.py additions: thresholds (anomaly, sleep variance), windows (trend), flags (ENABLE_PLAN_ENGINE, ENABLE_INSIGHT_CARD, ENABLE_COACH_CHIP)

7) Observability
- Counters appended to ops metrics: plan_generated, plan_skipped_missing_data, adherence_logged

8) Privacy
- Extend privacy scan to include new files; ensure no raw metrics are exported (only deltas/flags)

## Thresholds (defaults)
- Anomaly if any:
  - rhr_delta_7d ≥ +7 bpm OR sleep_hours < 6.5h OR stress_high OR (sugar_flag AND hrv_delta < 0)
- Sleep variance coach: 14d avg > 60m; target ±30m
- Steps trend down: 7d slope negative and below baseline

## Tests
- Unit tests for PlanEngine boundaries: anomaly precedence, rhrΔ=+7, sleep=6.5h, band consistency (no hard on anomaly), missing metrics fallback.
- Persistence tests: idempotent write, recompute flag behavior, timezone/DST basic guard.
- Web import tests (unit/e2e-lite): JSON schema validation, IndexedDB upsert, QR payload decode happy path.

## Tasks
- [ ] PlanEngine: finalize module and tests (done) and keep thresholds centralized
- [ ] Persistence: plan_daily.jsonl, adherence_daily.jsonl via atomic utilities (done)
- [ ] Morning job: generate plan before metrics; idempotent; ENABLE_PLAN_ENGINE guard (done)
- [ ] On-device UI: Plan card, chips, Done/Snooze, energy modal (minimal)
- [ ] Web import stub: QR scan + paste input page; JSON schema; IndexedDB helper
- [ ] Sample packet: add docs/specs/insight_packet_v1.sample.json for dev/testing
- [ ] Metrics/alerts: plan metrics in Prometheus; soft alert if no plan today (done)
- [ ] Privacy scan: include new files and packet schema; verify green
- [ ] Docs: Link ADR-0005 and web import spec from README and phase_5_issue; update CHANGELOG

## Acceptance criteria
- Plan emits ≤3 actions, renders <300ms from cached data
- Never emits hard plan on anomaly days
- One plan per local day; recompute requires explicit flag
- Privacy scan green, ops workflows continue to pass

## References
- PHASE_5_USER_STORIES_REVIEW.md
- docs/adr/ADR-0005-local-insight-packet-qr.md
- docs/specs/QR-Insight-Packet-and-Web-Import.md
- docs/PRD.md (Section 7.2 formulas)
- .github/workflows/daily-ops.yml
- phase_3_2_issue.md, phase_3_3_issue.md, phase_4_issue.md
