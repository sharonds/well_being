# ADR-0005: Local Compute + QR Insight Packet (No Companion App)

Date: 2025-08-13
Status: Proposed
Decision Makers: @sharonds

## Context
- Current blocker: Automated Garmin Connect ingestion is constrained by MFA and ToS; scraping is brittle and high-maintenance.
- iOS constraint: Building and maintaining a separate iOS companion app increases surface area and long-term costs.
- Repo status: Phase 5A PlanEngine is implemented with deterministic rules and local persistence; ops workflows are stable.
- Goal: Ship Phase 5 insights quickly with minimal moving parts, privacy-first, and high reliability.

## Decision
Adopt a watch-only computation flow with a “tiny insight packet” shared to the web app via QR scan (and optional copy/paste). Do not build an iOS companion app at this stage. Do not implement daily MFA-based scraping.

## Rationale (first principles)
- Reliability: Avoid brittle logins and hidden APIs; the watch already computes the plan. QR scan is deterministic and offline-friendly.
- Simplicity: Reduce components to two surfaces (watch + web). No companion app, no server needed to ship.
- Privacy: Share only minimal deltas/plan; no raw health streams.
- Speed: Enables immediate shipping of Phase A and Phase B UX.

## Alternatives Considered
- Daily MFA in web app: High friction, brittle, potential ToS/captcha issues, user becomes reliability layer.
- Garmin SDK companion app (iOS): Supported but higher complexity and maintenance; not needed for Phase A insights.
- Garmin Health API: Ideal long-term, requires approval/time; keep as future option.

## Consequences
- Pros: Fewest moving parts; fast to deliver; privacy-preserving; no MFA.
- Cons: Manual step (scan or paste) each morning; larger payloads may need multi-QR or compression in future (mitigated by tiny packet design).
- Future: Can add serverless endpoint later for one-tap sync; can adopt Health API without replacing QR path.

## Scope (now)
- Watch app renders QR with insight_packet_v1 (≤1KB) and a short code for copy.
- Web app scans/imports packet and stores locally (IndexedDB). No backend required.

## Out of Scope (now)
- iOS companion app, background sync, server ingestion, Garmin Health API integration.

## Success Criteria
- User can view Today + history in web app by scanning a QR or pasting a packet in <10s daily.
- No raw metric leakage; privacy scan remains green.
- PlanEngine outputs map 1:1 to visible copy.

## Rollback
- If QR proves too inconvenient, introduce Stage 1: a tiny serverless endpoint for one-tap upload from a later mobile companion or manual paste to endpoint.

## References
- Phase 5A PlanEngine: dashboard/scripts/plan_engine.py
- Phase A user stories: PHASE_5_USER_STORIES_REVIEW.md, phase_5_issue.md
