# Garmin Well-Being MVP

A Connect IQ watch app that provides daily readiness scoring based on wellness metrics.

## 🤖 Automation-First Development

This project showcases **end-to-end development automation**. Most features are implemented via GitHub Actions workflows rather than manual coding.

### Quick Start Automation (5 minutes)
```bash
# Your first automation
gh workflow run simple-automation.yml \
  --field task_name=error-codes \
  --field issue_number=NEW_ISSUE_NUMBER

# Monitor progress  
gh run list --limit 3
gh pr list --limit 2
```

**📚 Complete guides**: `AUTOMATION_QUICKSTART.md` | `AUTOMATION_PLAYBOOK.md` | `AUTOMATION_TEMPLATES.md`

## Current Phase

**Phase 1-3:** ✅ Complete (Basic score engine → Full feature MVP)  
**Phase 4:** 🤖 **Automated** - Production integration via micro-issue automation

### Phase 1 Delivered
- Score Engine (steps + resting HR, weight redistribution)
- Recommendation Mapping (3 bands)
- Metric stubs
- Manual Refresh + 5-minute throttling
- Minimal UI (score, metrics, recommendation)

### Phase 2 Goals
- Add sleep & stress metrics (graceful fallback)
- Persistence (lastScore, lastScoreDate) & delta display
- Example B test & redistribution permutations
- Feature flags: ENABLE_SLEEP, ENABLE_STRESS (default off)

## 🎯 Automation Status

**GitHub Copilot Coding Agent Pipeline: ACTIVE**
- ✅ Issue #1 created with enhanced PRD section references  
- ✅ Repository configured with branch protection and CI/CodeQL
- ✅ Coding Agent assigned and ready for systematic implementation
- 🔄 Automated development now in progress - monitoring phase

The project is now fully automated! The Coding Agent will:
1. Create feature branches for each Phase 1 task
2. Implement Connect IQ app functionality per PRD specifications  
3. Submit PRs with CI validation and tests
4. Progress through phases systematically

## Phase 1 Implementation Status

✅ **Completed Features:**
- **Score Engine**: Computes readiness score (0-100) from steps and resting heart rate
- **Recommendation Mapping**: Maps scores to actionable guidance
- **Metric Interface**: Stubbed data access for Phase 1 metrics
- **Manual Refresh**: User-triggered score recomputation with 5-minute throttling
- **Minimal UI**: Displays score, metrics, and recommendation

## Architecture

### Core Components

- **`WellBeingApp.mc`**: Main application and UI view
- **`ScoreEngine.mc`**: Score calculation with weight redistribution logic
- **`RecommendationMapper.mc`**: Maps scores to recommendation bands
- **`MetricProvider.mc`**: Metric access interface (Phase 1 stubs)

### Score Calculation (Phase 1)

Uses only steps and resting heart rate with weight redistribution:

```
Original weights: steps=0.40, resting_hr=0.30
Redistributed: steps=0.5714, resting_hr=0.4286

steps_norm = min(steps, 12000) / 12000
rhr_inv_norm = (80 - clamp(rhr, 40, 80)) / 40

score = (0.5714 * steps_norm + 0.4286 * rhr_inv_norm) * 100
```

### Recommendation Bands

- **0-39**: "Take it easy"
- **40-69**: "Maintain"  
- **70-100**: "Go for it"

## Usage

1. **Manual Refresh**: Press START key to recompute score
2. **Throttling**: Recomputation limited to once per 5 minutes
3. **Display**: Shows current score, steps, resting HR, and recommendation

## Testing

Run tests with: `bash scripts/run_tests.sh`

Validates:
- PRD test vectors (Example A: 8000 steps, 55 BPM → Score 65)
- Recommendation band boundaries
- Edge cases and error handling

## Build

Simulated build: Creates `build/WellBeing.prg` placeholder

For actual Connect IQ build:
```bash
monkeyc -o build/WellBeing.prg -f source/manifest.xml -y developer_key.der -w
```

## Test Vectors (Authoritative Examples)

| Case | Steps | Resting HR | Expected Score | Band | Status |
|------|-------|------------|----------------|------|--------|
| A | 8,000 | 55 | 65 | Maintain | ✅ |
| C | 3,000 | 70 | 25 | Take it easy | ✅ |
| Min | 0 | 80 | 0 | Take it easy | ✅ |
| Max | 12,000+ | 40 | 100 | Go for it | ✅ |
| B | 12,500 | 48 | 88 | Go for it | (Pending Phase 2 enable) |

## Roadmap

- **Phase 2** (current): Sleep, stress, persistence, delta
- **Phase 3**: Morning auto-refresh, HRV toggle, settings
- **Phase 4**: Polish, performance optimization

## Development

- **Language**: Monkey C (Connect IQ SDK 7.2.0)
- **Target**: Forerunner 965 (with graceful degradation)
- **Type**: Watch App

## Disclaimer
Not medical advice. Personal experimentation only.