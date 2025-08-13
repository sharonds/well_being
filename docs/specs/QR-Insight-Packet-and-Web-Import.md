# QR Insight Packet and Web Import – One-Pager

Date: 2025-08-13
Status: Draft
Owner: @sharonds

## Purpose
Enable the web app to show Today + history without MFA, companion apps, or servers by importing a tiny, privacy-preserving packet from the watch via QR (or paste).

## User flow
1) Morning: Watch computes plan (already implemented, Phase 5A).
2) Watch shows a QR labeled “Send to Web.”
3) User opens the web app, taps “Import,” and scans the QR (or pastes JSON).
4) Web app stores the packet locally and renders Today + history.

## Packet: insight_packet_v1 (≤1KB)
Envelope
- version: "v1"
- type: "plan_daily" | "adherence_daily"
- device_id: short hash (optional)
- created_at: ISO8601
- payload: object (below)

Payloads
- plan_daily:
  - date: YYYY-MM-DD
  - band: "Take it easy" | "Maintain" | "Go for it"
  - score: 0-100
  - delta: integer (today - yesterday)
  - plan: { type: "easy"|"maintain"|"hard", minutes_range: "30-40", addons: ["core10","breath10","nsdr","walk"] }
  - why: ["sleep −1.2h","RHR +6"] (≤2 reasons)
  - schema_version: "v1.0.0"
- adherence_daily (optional):
  - date: YYYY-MM-DD
  - actions_done: ["core10","breath10"]
  - energy_1_10: integer
  - logged_at: ISO8601

Constraints
- Max ~800–1000 bytes; prefer short keys where safe; base64+gzip optional later.
- No raw series; deltas/flags only.

## Web app import (zero-backend)
- Import UI: "Scan QR" and "Paste JSON".
- Storage: IndexedDB (key: insight:{date}:{type}); idempotent upsert (latest created_at wins).
- Rendering: Today view + simple history list.
- Validation: JSON schema check; version-gated parsing; ignore unknown fields.

## Watch UI
- QR: Single code for the day’s plan (plus optional adherence later).
- Fallback: Show a short alphanumeric code with a “Copy” action to display JSON for manual paste.

## Edge cases
- Scan fails: Offer paste input; keep a retry link.
- Multiple packets same day: last write wins; display a small “updated” badge.
- Large payload: drop to essentials (plan + why); split adherence if needed.

## Security & privacy
- No credentials or PII; optional device_id hash.
- Optional HMAC signature field later if server endpoint is introduced.
- Pass privacy scan (no raw metrics, no secrets).

## Metrics (optional UI-only)
- Count imported packets and distinct days; no network.

## Roadmap (optional)
- v1.1: support focus_update packet.
- Stage 1: add tiny serverless endpoint for one-tap upload; keep QR/paste as fallback.

## Dependencies
- PlanEngine outputs: dashboard/scripts/plan_engine.py
- Web app: camera access for QR (with permission), JSON validation, IndexedDB helper.
