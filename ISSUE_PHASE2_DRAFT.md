# Phase 2 Issue Draft (Do Not Delete Until Opened as Issue)

## Summary
Introduce sleep & stress metrics (feature-flagged), persistence (lastScore, lastScoreDate), delta display, and expanded tests (Example B + redistribution permutations) while preserving Phase 1 score compatibility when flags disabled.

## Objectives
- Sleep & stress metrics behind ENABLE_SLEEP / ENABLE_STRESS (default off)
- Weight redistribution across (steps, restingHR, sleep, stress)
- Persistence keys: lastScore (int), lastScoreDate (YYYYMMDD)
- Delta display (hide if no prior day)
- Add Example B test (Score 88) + permutations (each missing single metric)
- Backward compatibility guarantee

## Acceptance Criteria
| ID | Criterion | Ref |
|----|-----------|-----|
| AC1 | Enabling flags computes new weights without crash | PRD 7.2 |
| AC2 | Disabling flags yields EXACT original Phase 1 scores | PRD 7.2 |
| AC3 | Example B test passes (score 88) | PRD 14.1 |
| AC4 | Permutation tests pass (each missing metric case redistributes) | PRD 7.2 |
| AC5 | Persistence stores & loads lastScore & lastScoreDate | PRD 7.4 |
| AC6 | Delta hidden when no prior day stored | PRD 7.4 |
| AC7 | No test regressions (A=65, C=25) | PRD 14.1 |
| AC8 | Documentation updated (README, PRD phase status, execution_plan, copilot-instructions, lessons_learned) | Repo Docs |
| AC9 | Corrupted persistence (bad date or non-int score) ignored without crash; delta suppressed | PRD 7.4 |
| AC10 | Sum of active weights == 1.0 ±0.0001 (asserted) | PRD 7.2 |

## Non-Goals
- HRV integration
- Multi-day history beyond previous day
- Settings UI beyond feature flags constants

## Implementation Steps
1. Add feature flag constants (ENABLE_SLEEP / ENABLE_STRESS) default false.
2. Introduce SleepMetricProvider & StressMetricProvider (nullable returns, try-catch wrappers).
3. Extend ScoreEngine: incorporate metrics conditionally; compute activeWeights by presence & flag status.
4. Add normalization functions (sleep: min(hours,8)/8; stress: 1 - clamp(stress,0,100)/100).
5. Persistence: read/store lastScore & lastScoreDate at app start & after score computation on date change.
6. Delta logic: if stored date != today after compute, persist and hide delta this cycle; else show difference.
6a. Add central helper formatTodayYYYYMMDD() (no locale substring hacks) with shape test (length=8, numeric).
7. Tests: Example B (all metrics), permutations (missing each single metric), existing A & C unchanged with flags off.
8. README & execution_plan: ensure Phase 2 documented (already updated pre-implementation).
9. Update lessons learned checklist entries post-merge.

## Contracts
- lastScoreDate format: YYYYMMDD (local device date)
- Rounding: floor(x + 0.5)
- Active Weight Formula: baseWeight / sum(baseWeights present)
- Base Weights (all present): steps 0.40, restingHR 0.30, sleep 0.20, stress 0.10

## Edge Cases
- Missing both new metrics: identical behavior to Phase 1.
- Only one of sleep/stress available (other null): redistribute among available subset.
- Persistence file corruption: ignore & reinitialize (log warning).
- Midnight rollover while app open: next manual refresh triggers delta logic with new date.
- Stored date == today but lastScore missing/null: treat as first day (hide delta, initialize new values).
- Prior score equals current score: delta = 0 still displayed when available.

## Testing Plan
Example B explicit inputs: steps=12500 (cap 12000), restingHR=48, sleep=7h, stress=35 => expected 88.

Scenarios (enumerated):
1. All metrics present (flags ON) -> Example B = 88
2. Missing Sleep only (sleep null or flag off) -> redistribute; verify score matches dynamic formula and weight sum tolerance
3. Missing Stress only -> redistribute; verify
4. Missing Sleep & Stress -> score equals Phase 1 for same steps/restHR inputs (e.g., Examples A & C)

Backward compatibility suite (flags OFF): Examples A=65, C=25 must match golden values exactly.

Additional assertions:
- Sum(activeWeights) within ±0.0001 of 1.0 for every permutation.
- Corrupted persistence simulation: inject invalid lastScore (string) or date (length !=8) => no crash, delta suppressed.
- Band transition tests (39/40, 69/70) unchanged.
- Rounding check: construct raw producing x.49 and x.50 boundaries to ensure floor(x+0.5) rule.

Test harness requirements:
- Fails build if any assertion fails.
- Outputs sentinel line "Tests: X/Y passed" already present; ensure non-100% triggers non-zero exit.

## Risks & Mitigations
| Risk | Mitigation |
|------|------------|
| Weight drift when flags off | Snapshot Phase1 expected scores; assert equality |
| Null metric crash | Defensive null checks + try-catch |
| Date handling mismatch | Central helper for YYYYMMDD formatting |
| Silent weight sum error | Explicit sum(activeWeights) assertion |
| Persistence corruption hides regression | Corruption test ensures graceful handling & logging |

## Definition of Done
- All acceptance criteria met
- CI green (tests + CodeQL)
- Documentation updated and consistent
- PR references PRD sections & includes test output

## Post-Merge Follow Ups (Not Blocking)
- Evaluate adding HRV (Phase 3 planning)
- Consider multi-day trend storage

(End of Draft)
