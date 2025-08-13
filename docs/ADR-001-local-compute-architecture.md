# ADR-001: Local Compute with Insight Packet Architecture

Date: 2025-08-13
Status: Accepted

## Context

The wellness dashboard needs to deliver personalized daily training plans and insights to users on mobile devices (primarily iPhone). We need to decide on the architecture for compute, data flow, and user experience.

## Decision

We will adopt a **"Local compute + tiny insight packet"** architecture with the following principles:

1. **Local-first compute**: All plan generation and scoring happens locally on the device or in the daily-ops workflow
2. **Tiny insight packets**: Export minimal JSON packets (<1KB) containing just the daily plan and key metrics
3. **Server optional**: The system works without a backend server initially
4. **Health API later**: Integration with Apple Health API deferred to future phase

## Architecture Components

### Stage 0: Insight Packet (Current)
```
Daily Ops (GitHub Actions)
    ↓
Generate Plan & Metrics
    ↓
Export JSON packet
    ↓
QR Code / URL
    ↓
iPhone imports packet
```

### Stage 1: One-tap Sync (Future)
```
iPhone App
    ↓
Fetch from GitHub/CDN
    ↓
Local compute refinement
    ↓
Display plan
```

### Stage 2: Health API Integration (Future)
```
Apple Health API
    ↓
Real-time metrics
    ↓
Local PlanEngine
    ↓
Instant updates
```

## Rationale

### Why Local Compute?

1. **Privacy**: Health data never leaves the device unnecessarily
2. **Performance**: Instant plan generation (<300ms)
3. **Offline-first**: Works without internet after initial sync
4. **Cost**: No server infrastructure needed initially
5. **Simplicity**: Reduced complexity, no API authentication

### Why Insight Packets?

1. **Minimal data transfer**: ~500 bytes per day
2. **Easy distribution**: QR codes, URLs, or manual entry
3. **Version control**: Packets can be versioned
4. **Debugging**: Easy to inspect and validate

### Why Server Optional?

1. **Fast iteration**: Ship iPhone app without backend
2. **Progressive enhancement**: Add server features later
3. **Fallback**: GitHub Actions as "serverless" compute
4. **Cost effective**: No hosting costs initially

## Implementation

### Current (Phase 5A)
- ✅ PlanEngine runs in daily-ops workflow
- ✅ Generates plan_daily.jsonl locally
- ✅ Metrics exported to JSON

### Next Steps (Phase 5B-D)
- Export insight packet endpoint
- Generate QR code for daily plan
- iPhone app imports packet
- Local storage on device

### Example Insight Packet
```json
{
  "date": "2025-08-13",
  "plan": {
    "type": "maintain",
    "minutes": "45-60",
    "text": "Steady 45-60m + Core 10m. Why: stable sleep/RHR",
    "addons": ["core", "breath"]
  },
  "metrics": {
    "score": 65,
    "band": "Maintain",
    "rhr_delta": 2,
    "sleep_hours": 7.5
  },
  "version": "1.0.0"
}
```

## Consequences

### Positive
- **Fast deployment**: iPhone app can ship without backend
- **Privacy-preserving**: Health data stays local
- **Cost-effective**: No server costs initially
- **Reliable**: No server downtime affects users
- **Simple**: Fewer moving parts to maintain

### Negative
- **Limited sharing**: No easy multi-device sync initially
- **Manual updates**: Users must fetch daily packets
- **No push notifications**: Without server, no push capability
- **Analytics limited**: No centralized usage data

### Mitigations
- **Future server**: Can add optional server sync later
- **iCloud sync**: Use iCloud for multi-device support
- **Local notifications**: Schedule on-device reminders
- **Anonymous telemetry**: Optional privacy-preserving analytics

## Alternatives Considered

1. **Server-first**: Rejected due to complexity and privacy concerns
2. **Direct Health API**: Rejected as Stage 0 (too complex initially)
3. **Web-only**: Rejected (poor mobile experience)
4. **Native only**: Rejected (no web fallback)

## References
- Phase 5 Issue: phase_5_issue.md
- User Stories: PHASE_5_USER_STORIES_REVIEW.md
- Privacy Requirements: dashboard/scripts/privacy_scan.py

## Review
- Reviewed by: ChatGPT-5
- Approved by: @sharonds
- Implementation: Phase 5A complete