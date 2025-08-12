# Garmin Well-Being MVP

A Connect IQ watch app that provides daily readiness scoring based on wellness metrics.

## Current Status

### ✅ Phase 1: COMPLETE (PR #2)
- Score Engine with steps + resting HR
- Recommendation Mapping (3 bands)
- Manual Refresh with 5-minute throttling
- Basic UI display
- Test harness and validation

### ✅ Phase 2: COMPLETE
- Sleep & Stress metrics added (with graceful fallback)
- Persistence layer (lastScore, lastScoreDate)
- Delta display showing score change
- Weight redistribution for missing metrics
- Feature flags: ENABLE_SLEEP, ENABLE_STRESS (default off)

### ✅ Phase 3: COMPLETE (PR #7)
- Morning auto-refresh scheduler (7-11am)
- Structured logging system (Logger.mc)
- HRV feature flag (not implemented)
- Background processing support
- Enhanced error handling

### ⚠️ Phase 4: PARTIALLY COMPLETE
**Implemented:**
- ✅ Clock abstraction with real time APIs (AC2)
- ✅ Real resting HR via UserProfile (AC1 partial)
- ✅ ErrorCodes structure for logging (AC4)
- ✅ Settings menu for runtime toggles (AC7)
- ✅ Performance timer utility (AC8)
- ✅ Comprehensive test suite (AC10)

**Not Implemented:**
- ❌ Real steps via ActivityMonitor (AC1 partial)
- ❌ 7-day history buffer (AC6)
- ❌ Enhanced UI indicators (AC5)
- ❌ Full documentation updates (AC9)

## Development Approach

### Automation Tools Available
- **GitHub Actions**: Simple automation workflow for micro-issues
- **Copilot Code Review**: Systematic PR review with pre-gates validation
- **Test Suite**: Comprehensive validation via `./scripts/run_tests.sh`

### Key Commands
```bash
# Run tests
./scripts/run_tests.sh

# Prepare for Copilot review
./scripts/prepare-copilot-review.sh

# Create micro-issue automation
gh workflow run simple-automation.yml \
  --field task_name=<name> \
  --field issue_number=<number>
```

## Architecture

### Core Components

- **`WellBeingApp.mc`**: Main application, UI view, and persistence
- **`score/ScoreEngine.mc`**: Score calculation with weight redistribution
- **`RecommendationMapper.mc`**: Maps scores to recommendation bands
- **`MetricProvider.mc`**: Metric access with partial real API integration
- **`clock/Clock.mc`**: Real time/date abstraction
- **`Scheduler.mc`**: Auto-refresh scheduling logic
- **`Logger.mc`**: Structured logging system
- **`ErrorCodes.mc`**: Error code constants
- **`SettingsMenu.mc`**: Runtime feature toggles
- **`PerformanceTimer.mc`**: Performance measurement utility

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