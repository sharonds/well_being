# WellBeing Garmin Connect IQ App

A personal well-being tracking app for Garmin watches that computes daily readiness scores based on health metrics.

## Status: Phase 3 Complete ✅

- **Phase 1**: ✅ Basic score engine (steps + resting HR), manual refresh, throttling
- **Phase 2**: ✅ Sleep & stress metrics, persistence, feature flags  
- **Phase 3**: ✅ Morning auto-refresh, logging, HRV integration, enhanced error handling

## Features

### Core Functionality
- **Daily Readiness Score (0-100)**: Computed from available health metrics
- **Recommendation Bands**: "Take it easy" (0-39), "Maintain" (40-69), "Go for it" (70-100)
- **Weight Redistribution**: Automatically adjusts when metrics unavailable
- **5-Minute Throttling**: Prevents excessive refreshes

### Phase 3 Features
- **Morning Auto-Refresh**: Automatic score computation once daily (06:00-08:00)
- **Enhanced Error Handling**: Graceful fallback when individual metrics fail
- **Logging Ring Buffer**: Captures last 20 diagnostic events with timestamps
- **HRV Integration**: Optional HRV metric with ENABLE_HRV feature flag
- **Performance Monitoring**: < 50ms score computation with timing harness

### Supported Metrics
| Metric | Phase | Feature Flag | Weight (no HRV) | Weight (with HRV) |
|--------|-------|--------------|-----------------|-------------------|
| Steps | 1 | Always On | 0.40 | 0.35 |
| Resting HR | 1 | Always On | 0.30 | 0.25 |
| Sleep Hours | 2 | ENABLE_SLEEP | 0.20 | 0.20 |
| Stress Level | 2 | ENABLE_STRESS | 0.10 | 0.10 |
| HRV (ms) | 3 | ENABLE_HRV | N/A | 0.10 |

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

- **`WellBeingApp.mc`**: Main application with auto-refresh logic and enhanced error handling
- **`ScoreEngine.mc`**: Score calculation with dynamic weight redistribution and HRV support
- **`RecommendationMapper.mc`**: Maps scores to recommendation bands
- **`MetricProvider.mc`**: Metric access interface with graceful error handling
- **`Logger.mc`**: Ring buffer logging system (20 entries)
- **`Scheduler.mc`**: Auto-refresh scheduling and window detection
- **`PerformanceTimer.mc`**: Performance measurement and validation

### Score Calculation (All Phases)

**Phase 1** (steps + resting HR only):
```
Redistributed weights: steps=0.5714, resting_hr=0.4286
score = (0.5714 * steps_norm + 0.4286 * rhr_inv_norm) * 100
```

**Phase 2** (with sleep/stress when enabled):
```
Base weights: steps=0.40, rhr=0.30, sleep=0.20, stress=0.10
Active weights = base_weight / sum_of_present_metrics
```

**Phase 3** (with HRV when enabled):
```
Base weights: steps=0.35, rhr=0.25, sleep=0.20, stress=0.10, hrv=0.10
Active weights = base_weight / sum_of_present_metrics
HRV normalization: (hrv_ms - 20) / (120 - 20) for 20-120ms range
```

### Auto-Refresh System

- **Morning Window**: 06:00-08:00 local time
- **Single Daily Trigger**: Prevents duplicate auto-refreshes
- **Missed Window Detection**: Triggers refresh if app opened after 08:00
- **Throttle Integration**: Respects existing 5-minute minimum interval
- **Persistence**: Tracks autoRefreshDate and lastRunMode

### Recommendation Bands

- **0-39**: "Take it easy"
- **40-69**: "Maintain"  
- **70-100**: "Go for it"

## Usage

### Manual Operation
1. **Manual Refresh**: Press START key to recompute score
2. **Throttling**: Recomputation limited to once per 5 minutes
3. **Display**: Shows current score, metrics, and recommendation

### Automatic Operation (Phase 3)
1. **Morning Auto-Refresh**: Automatically computes score once daily between 06:00-08:00
2. **Missed Window**: If app opened after 08:00 without today's score, triggers refresh
3. **Error Handling**: Individual metric failures logged but don't crash app
4. **Performance Monitoring**: Computation times logged and validated < 50ms

## Testing

Run all tests: `bash scripts/run_tests.sh`
Run Phase 3 validation: `bash scripts/validate_phase3.sh`

Validates:
- All PRD test vectors (Examples A, B, C)
- HRV integration and weight redistribution
- Auto-refresh logic and timing
- Logger ring buffer behavior
- Performance requirements
- Backward compatibility across all phases

## Build

Simulated build: Creates `build/WellBeing.prg` placeholder

For actual Connect IQ build:
```bash
monkeyc -o build/WellBeing.prg -f source/manifest.xml -y developer_key.der -w
```

## Test Vectors (Authoritative Examples)

| Case | Steps | Resting HR | Sleep | Stress | HRV | Expected Score | Band | Status |
|------|-------|------------|-------|--------|-----|----------------|------|--------|
| A | 8,000 | 55 | -- | -- | -- | 65 | Maintain | ✅ |
| B | 12,500 | 48 | 7h | 35 | -- | 88 | Go for it | ✅ |
| C | 3,000 | 70 | -- | -- | -- | 25 | Take it easy | ✅ |
| Min | 0 | 80 | -- | -- | -- | 0 | Take it easy | ✅ |
| Max | 12,000+ | 40 | -- | -- | -- | 100 | Go for it | ✅ |

## Feature Flags

| Flag | Default | Phase | Description |
|------|---------|-------|-------------|
| ENABLE_SLEEP | false | 2 | Sleep hours metric integration |
| ENABLE_STRESS | false | 2 | Stress level metric integration |  
| ENABLE_HRV | false | 3 | HRV metric integration with weight adjustment |

## Roadmap - COMPLETE

- **Phase 1** ✅: Core score engine (steps + resting HR)
- **Phase 2** ✅: Sleep, stress, persistence, feature flags  
- **Phase 3** ✅: Auto-refresh, logging, HRV, enhanced error handling
- **Future**: UI polish, additional metrics, settings screen

## Development Status

✅ **All Requirements Complete**
- All PRD test vectors pass
- All 10 Phase 3 acceptance criteria met
- Backward compatibility maintained
- Performance requirements satisfied
- Comprehensive test coverage

## Development

- **Language**: Monkey C (Connect IQ SDK 7.2.0)
- **Target**: Forerunner 965 (with graceful degradation)
- **Type**: Watch App

## Disclaimer
Not medical advice. Personal experimentation only.