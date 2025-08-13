# Phase 5 – User Stories Review and Recommendations

Date: 2025-08-13
Author: Copilot Agent
Status: Draft (for implementation handoff)

## Summary
Your Phase 5 user stories are strong: single-screen clarity, deterministic-first rules, tight acceptance criteria, and phased delivery. They align with the existing scoring engine, ops guardrails, and privacy constraints. Below are pragmatic recommendations to keep scope tight for Phase A while laying safe foundations.

## What’s great
- One “Today” screen with a single plan and Tier-1 chips keeps decisions simple.
- Deterministic rules before adaptive logic; AI limited to copy summarization.
- Clear acceptance criteria (e.g., render <300ms, ≤3 actions, never hard on anomaly days).
- Phased rollout (A→D) enables learning without heavy upfront cost.

## Gaps to cover pre-implementation
- Centralize thresholds: anomaly (RHRΔ, sleep hours, stress), sleep variance target, steps trend window; avoid drift across modules.
- Data availability: HRV and sugar flag may be missing; design graceful fallback paths so Phase A does not depend on them.
- Idempotent morning job: Ensure “one plan per local day” with atomic writes and DST handling.
- Guardrail: If anomaly=true, never emit “hard” plans—enforce in the plan engine, not only in UI copy.
- Privacy: New adherence/energy signals must remain local-first and pass the privacy gate.

## Proposed minimal contracts
- PlanEngine input: {band, score, delta, rhr_delta_7d, sleep_hours, sleep_var_14d, stress_midday|daily, steps_trend_7d, hrv_delta?, sugar_flag?}
- PlanEngine output: {plan_type: easy|maintain|hard, minutes_range, addons: [core|breath|nsdr|walk], why: [top1–2 deltas], triggers: [coach|nudge]}
- Missing metrics: degrade to conservative “Easy” and log reason; never crash.

## Default thresholds (tunable via config)
- Anomaly if any true:
  - rhr_delta_7d ≥ +7 bpm OR
  - sleep_hours < 6.5h OR
  - stress_high (top-decile day or > configured threshold) OR
  - (sugar_flag AND hrv_delta < 0)
- Sleep variance coach: fire when 14d average bedtime variance > 60m (target ±30m).
- Steps trend down: 7d slope negative and below baseline floor.

## Phase A scope (ship fast)
- PlanEngine module + tests for anomaly rule precedence and boundary thresholds.
- Idempotent morning job that persists plan once per local day (atomic write, backups).
- Minimal UI: Plan card with copy-kit templates, Tier-1 chips, Done/Snooze; energy 1–10 modal.
- “Why” sentence from top deltas if available; otherwise conservative explanation.
- Light observability counters: plan_generated, plan_skipped_missing_data, adherence_logged.
- Privacy scan updated to include new schemas; no raw metric leakage.

## Risks and mitigations
- Missing metrics → conservative Easy plan + “Using last known metrics.”
- Nudge vs plan conflicts → suppress nudge if it overlaps; plan takes precedence.
- Timer complexity → defer “Start” timer to later phase; keep Done/Snooze only in Phase A.

## References
- PRD: docs/PRD.md (weights and bands; Section 7.2 formulas)
- Ops & SLOs: docs/SLOs.md; .github/workflows/daily-ops.yml
- Prior phases: phase_3_2_issue.md, phase_3_3_issue.md, phase_4_issue.md
