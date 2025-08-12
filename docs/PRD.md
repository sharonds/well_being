# Product Requirements Document (PRD)

## 0. Meta
- Product Name: (TBD) Garmin Well-Being MVP
- Owner: You (personal project)
- Created: 2025-08-12
- Status: Phase 1-3 COMPLETE / Phase 4 90% COMPLETE (v0.9)
- Canonical Location: /docs/PRD.md

## 1. Purpose / Problem Statement
Improve personal daily well-being by capturing a small, high-signal set of metrics from a Garmin wearable and surfacing a simple on-device daily score + actionable nudge, with iteration speed prioritized over polish.

## 2. Primary User & Use Case
- User: Single individual (you). No multi-user, no distribution.
- Context: Morning review + occasional daytime glances.
- Device Target: Garmin watch (Connect IQ) model TBD (must support required sensors listed below).

## 3. MVP Vision (Concise)
Deliver a watch app (or data field/widget depending on feasibility) that:
1. Collects a minimal set of metrics (resting HR, sleep duration proxy, step count, HRV if accessible via API, body battery / stress if available) for the last 24h or previous night.
2. Computes a simple Daily Readiness Score (0–100) using a transparent formula.
3. Shows: Score, 2–3 key raw metrics, and one short recommendation ("Light recovery day" / "Good to push" / etc.).
4. Persists last score locally for comparison (no cloud sync in MVP).
5. Updates on demand (manual refresh) and once automatically in the morning window (e.g., 06:00 local or on first launch after 5am).

## 4. Non-Goals (Out of Scope for MVP)
- Multi-user support or account system.
- Cloud storage / external API sync.
- Historical charting > last 2 days.
- Advanced ML/AI modeling; only deterministic formula.
- Notifications / background push alerts (beyond what is trivially allowed if any).
- Mobile companion app.
- Localization / multi-language.
- Monetization, sharing, or social features.

## 5. Feature List (MVP)
| ID | Feature | Description | Acceptance Criteria (High-Level) |
|----|---------|-------------|----------------------------------|
| F1 | Sensor Data Access | Access required metrics from device APIs. | All needed metrics fetched or gracefully defaulted; failure fallback logged; no crashes. |
| F2 | Readiness Score Engine | Deterministic formula combining normalized metrics. | Score always between 0–100; formula documented; unit tests cover edge cases. |
| F3 | Recommendation Generator | Map score bands to short textual guidance. | Text matches defined banding rules; unit tested. |
| F4 | Daily Refresh Logic | One auto morning refresh + manual refresh action. | Auto refresh occurs once; manual refresh triggers recompute; debounced to avoid spam. |
| F5 | Simple UI Display | Compact screen: score, 2–3 metrics, recommendation. | Renders within device constraints; readable in default theme; handles missing metric state. |
| F6 | Local Persistence | Store prior day score for delta comparison. | Previous value shows delta arrow or sign; persists across app restarts. |
| F7 | Basic Settings (Optional toggle) | Allow user to enable/disable HRV usage if unstable. | Toggle stored; score adjusts accordingly. |

### 5.1 Implementation Parameters (Fixed for MVP)
| Item | Decision | Rationale |
|------|----------|-----------|
| App Type | Connect IQ Watch App (not widget/data field) | Full-screen control; simpler iterative UI changes. |
| Target Device (primary) | Forerunner 965 | Modern model with HRV, stress, body battery support. |
| Secondary Compatibility | Graceful degradation on devices lacking HRV/stress; still function with steps + resting HR. | Wider future reuse. |
| Connect IQ SDK Version | 7.2.0 (min API Level matching FR965 capabilities) | Current enough for health metrics; adjust if needed. |
| Language | Monkey C | Standard for Connect IQ. |
| Manual Refresh Trigger | Press START/SELECT key while in app (Phase 1) | Intuitive & minimal UI complexity. |
| Auto Refresh | Deferred to Phase 3 (morning logic) | Keeps Phase 1 minimal. |
| Time Source | Device local time (no DST special handling) | Simplicity; acceptable for personal use. |
| Storage Mechanism | App Properties (key-value) | Lightweight persistence for few keys. |
| Stored Keys | lastScore (int), lastScoreDate (YYYY-MM-DD), lastScorePrev (int, optional) | Supports delta & day change. |
| Score Recompute Throttle | Minimum 5 minutes between manual recomputes unless forced on first load | Battery protection. |
| Logging Buffer | In-memory ring buffer of last 20 log lines (not persisted) | Debug without long-term storage. |
| HRV Toggle Location | Settings screen (Phase 3) | Avoid cluttering Phase 1 UI. |
| First-Run UI | Shows "--" for delta; metrics present; recommendation based on initial score | Clear initial state. |
| Medical Disclaimer | Short static line in About/Settings: "Not medical advice" | Risk clarity even for personal use. |
| Versioning | Semantic: v0.x until stable; display in debug/about screen | Clarity during iterations. |
| Color / Contrast | Use default theme colors; avoid low-contrast custom palette | Readability. |


## 6. Phased Delivery (Incremental)
Goal: Earliest end-to-end feedback ASAP.

### Phase 1 (Slice to Visual Feedback Fast) ✅ COMPLETE
- F1 (subset: steps, resting HR only)
- F2 (prototype formula using just steps + resting HR)
- F3 (basic 3-band recommendation)
- F5 (minimal UI)
Notes: No auto morning refresh yet (manual only). No persistence (delta) yet. No HRV/stress. Throttle enforced (5 min) to avoid rapid recomputes.
Acceptance: App runs, displays a score and recommendation using two metrics; manual refresh recalculates (respecting throttle) within 1 second.

### Phase 2 (Add Core Metrics & Persistence) 🚧 IN PROGRESS
- Extend F1: add sleep duration proxy & stress/body battery (or stress score) if accessible
- Refine F2 formula weighting with new metrics (sleep + stress), apply weight redistribution
- Add F6 Persistence (store yesterday score) with keys: lastScore (int), lastScoreDate (YYYYMMDD)
- Enhance F5 UI to show delta and up/down indicator (hide if first day)
- Add Example B test + redistribution permutations

### Phase 3 (Stability & Morning Automation)
- Implement F4 auto morning refresh logic
- Add F7 settings toggle for HRV usage (if HRV added) or fallback handling
- Error handling / graceful defaults for missing data
- Unit test coverage expansion

### Phase 4 (Polish & Observability Light)
- Fine-tune bands & text wording (F3)
- Performance/battery sanity validation
- Add lightweight internal debug screen (metric raw values)
- Documentation & final acceptance review

## 7. Detailed Requirements
### 7.1 Metrics & Data Acquisition
List Garmin Connect IQ APIs to attempt (need confirmation):
- Steps: Toybox::Activity or Toybox::Sensor?
- Resting HR: Toybox::Health API (if available)
- Sleep duration: May require summary health; if unavailable, allow manual estimation (defer if unsupported in device)
- HRV: Potentially limited; treat as optional (behind toggle)
- Stress / Body Battery: Only if straightforward; else skip in Ph2.
Fallback values: If metric unavailable, mark as "--" and adjust formula weights proportionally.

### 7.2 Readiness Score Formula (Initial Draft)
Base (all metrics available):
score = clamp(0,100,
  0.40 * steps_norm + 0.30 * resting_hr_inv_norm + 0.20 * sleep_norm + 0.10 * stress_inv_norm )

Normalization Draft:
| Metric | Raw Assumed Range (Cap) | Normalization Function |
|--------|-------------------------|------------------------|
| Steps (24h) | 0 – 12,000 | steps_norm = min(steps,12000) / 12000 |
| Resting HR (bpm) | 40 – 80 | resting_hr_inv_norm = (80 - clamp(rhr,40,80)) / 40 |
| Sleep (hours) | 0 – 8 | sleep_norm = min(sleepHrs,8) / 8 |
| Stress (Garmin 0–100) | 0 – 100 | stress_inv_norm = 1 - (clamp(stress,0,100)/100) |
| HRV (ms, OPTIONAL) | 40 – 120 | hrv_norm = (clamp(hrv,40,120) - 40) / 80 |

If HRV enabled & available (Phase 3+), redistribute weights (example):
steps 0.35, resting_hr_inv 0.25, sleep 0.20, stress_inv 0.10, hrv_norm 0.10.

Missing Metric Weight Redistribution:
Remove missing metrics, sum remaining base weights, scale each remaining weight by (originalWeight / sumRemainingOriginalWeights).

Deterministic Test Vectors will use explicit inputs & expected outputs (see Appendix).

Throttle: Recomputes ignored if <5 minutes since last unless day rollover or first launch.

### 7.3 Recommendation Bands
| Range | Text |
|-------|------|
| 0–39 | "Take it easy" |
| 40–69 | "Maintain" |
| 70–100 | "Go for it" |

### 7.4 Persistence (Phase 2 Scope)
- Store last score & date in app storage (key-value).
- If prior day not found, show no delta indicator.
- Keys used (Phase 2 minimal): lastScore (int), lastScoreDate (YYYYMMDD string)
- Future (optional) lastScorePrev removed from Phase 2 to keep persistence minimal; can reintroduce if comparative history needed.

### 7.5 Morning Auto Refresh
- On app start: if current local date differs from stored date and time >= 05:00, trigger recompute once.
- Prevent double auto refresh in same day.
 - Not implemented until Phase 3.

### 7.6 Settings Toggle (HRV)
- Simple boolean in settings menu or inline toggle screen section.
- When disabled or unavailable, HRV dropped from formula and weights redistributed.

### 7.7 UI Layout (Baseline)
- Top: Score (large)
- Middle: metrics list (e.g., Steps, RestHR, SleepHrs or --)
- Bottom: Recommendation text
- Optional small delta arrow next to score (Phase 2+)
- Error state: "Data unavailable" placeholder.

### 7.8 Error Handling
- All metric fetch wrapped in try/catch; log minimal debug string (no PII) to internal buffer.
- Continue rendering with partial data.
 - If all metrics fail, still show lastScore (if any) else message: "Data unavailable".

### 7.9 Performance & Battery (Phase 4)
- Single on-demand fetch; no polling loop.
- Avoid heavy allocations per refresh.
- Target <50ms compute on typical device (informal measurement).

### 7.10 Logging / Debug (Phase 4)
- Hidden key combo or settings to open debug view listing raw metric values + last refresh time.

## 8. Acceptance Criteria (Consolidated)
1. Score always within 0–100; tests validate normalization and weight redistribution with missing metrics.
2. App never crashes when any single metric API fails (simulated tests or mocks pass).
3. Manual refresh recomputes within 1 second UI update (when not throttled).
4. Morning auto refresh triggers exactly once per day when conditions met (testable via injected clock or simulation).
5. Recommendation text matches defined band table for representative sample inputs.
6. Persistence shows previous day delta after Phase 2 implementation.
7. HRV toggle changes formula path (weight redistribution) immediately after change (Phase 3+).
8. Throttle prevents recompute spam (<5 min interval) while still allowing first-run or day-change recompute.
9. Logging buffer never exceeds 20 entries and oldest entries discarded first.

## 9. Testing Strategy
- Unit tests: formula, normalization, recommendation mapping, weight redistribution, persistence logic, auto refresh gating.
- Integration (simulated environment): end-to-end refresh with stubbed metric providers.
- Manual: on-device (or simulator) visual sanity + battery quick check.
- Edge test cases: all metrics missing, one metric extreme high/low, clock boundary (04:59 vs 05:00), duplicate refresh attempts.

## 10. Open Questions
- Exact Connect IQ APIs available for targeted device model? (Resolve before Phase 2.)
- HRV accessibility & reliability? (Decide by end Phase 2; else drop F7.)
- Sleep data feasible locally? If not, adjust formula weights earlier.

## 11. Risks & Mitigations
| Risk | Impact | Mitigation |
|------|--------|------------|
| Missing sensor APIs | Score lacks components | Design formula to degrade gracefully; toggle features off. |
| Over-engineering early | Delays feedback | Phase slicing; keep Phase 1 minimal. |
| Battery drain | User abandons app | Single-shot refresh; no background loops. |
| Unstable HRV | Erratic scores | Optional toggle; treat as bonus metric. |

## 12. Out-of-Scope Validation
Any request for history charts, ML predictions, cloud sync, notifications, or social features is rejected until post-MVP.

Medical Disclaimer: This app provides wellness-related estimates for personal experimentation only and is not medical advice.

## 13. Definition of Done (Per Phase)
- Phase criteria implemented + all related acceptance tests passing.
- No unresolved high-severity errors in logs for normal run.
- PR merged with green CI + CodeQL.
- Issue updated with checklist completion and any new bug items logged.

## 14. Appendix
### 14.1 Worked Examples (Draft)
Example A (Phase 1 metrics only):
Steps=8,000; RestingHR=55
steps_norm = 8000/12000 = 0.667
resting_hr_inv_norm = (80-55)/40 = 25/40 = 0.625
Weights Phase1 (no sleep, stress): redistribute original (steps 0.40, rhr 0.30) => sum=0.70
steps weight = 0.40/0.70 ≈ 0.5714; rhr weight ≈ 0.4286
score_raw = 0.5714*0.667 + 0.4286*0.625 ≈ 0.380 + 0.268 = 0.648
Score = 65 (rounded)
Band => 40–69 => "Maintain"

Example B (All metrics, no HRV) – authoritative test vector:
Steps=12,500 (cap 12,000) -> 1.0
RestingHR=48 -> (80-48)/40 = 32/40 = 0.8
Sleep=7h -> 7/8 = 0.875
Stress=35 -> 1 - 0.35 = 0.65
score = 0.40*1.0 + 0.30*0.8 + 0.20*0.875 + 0.10*0.65
  = 0.40 + 0.24 + 0.175 + 0.065 = 0.88 -> 88 => "Go for it"

Example C (Missing Sleep & Stress):
Available: Steps=3,000 (0.25), RestingHR=70 ((80-70)/40=0.25)
Remaining original weights: steps 0.40, rhr 0.30 => sum 0.70
Redistributed weights: steps 0.5714, rhr 0.4286
score = 0.5714*0.25 + 0.4286*0.25 = 0.25 -> 25 => "Take it easy"

### 14.2 Future Test Vector Table Template
| Case | Inputs (steps,rhr,sleep,stress,hrv,missing) | Expected Score | Band | Notes |
|------|---------------------------------------------|----------------|------|-------|
| A | 8000,55,--,--,--,sleep+stress | 65 | Maintain | Phase1 redistribution |
| B | 12500,48,7,35,--,none | 88 | Go for it | Caps & full weights |
| C | 3000,70,--,--,--,sleep+stress | 25 | Take it easy | Low metrics |

---
Draft additions applied. Adjust device / SDK if you prefer different targets.

---
Draft complete. Update user-specific details (device model, exact APIs) before Phase 2 planning.
