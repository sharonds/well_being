# T-001: On-watch QR Encoder (Bake-off Task)

Purpose: Replace the placeholder QR grid with a real, scannable alphanumeric QR code on the Garmin Connect IQ watch app, preserving the JSON fallback view. This is a small, high-signal task aligned with Phase 5 goals.

## Context
- App: Garmin Connect IQ Watch App (Monkey C)
- Target Device: Forerunner 965 (primary)
- SDK: 7.2.0
- Current State: `QRView.mc` shows a placeholder grid and lets users switch to JSON fallback.
- Packet: Built via `InsightPacket` builder; same data rendered in QR and JSON fallback.

See PRD sections 7.2, 7.4 and repo guardrails in `.github/copilot-instructions.md`.

## Requirements (Acceptance Criteria)
1. Functional
   - Display a scannable QR that encodes the current insight packet (alphanumeric JSON, UTF‑8, within QR version that fits device screen).
   - QR must scan reliably on a typical mobile browser (Chrome/Safari) under indoor lighting at arm’s length.
   - Keep JSON fallback view accessible and unchanged.
2. Compatibility & Stability
   - No regressions to Phase 1–4 behavior when feature flags are off.
   - App must not crash on missing metrics; fallback to JSON if QR generation fails.
3. Performance
   - Maintain compute path budget: score engine remains <50ms.
   - QR generation should complete within reasonable UI frame bounds; avoid jank.
4. Quality & Safety
   - Wrap API calls with try/catch and log errors to ring buffer (max 20 entries).
   - Do not introduce external network calls or unsafe dependencies.
5. Tests & Docs
   - Update/add a minimal test or harness stub validating QR payload content matches JSON fallback payload (string equality before encoding).
   - Add a concise “How to validate” section in PR description.

## Constraints
- Language: Monkey C
- Avoid large third‑party libs; prefer a minimal QR encoder suitable for Connect IQ.
- Files allowed to change:
  - `source/QRView.mc` (replace placeholder with QR rendering)
  - `source/InsightPacket.mc` (only if minor helper needed; preserve output schema)
  - Small utility under `source/utils/` if required (QR encoding math)
  - Tests under `tests/` (add minimal validation)
  - Docs under `docs/` (optional short note)
- Do NOT modify: `.gitignore`, `SECURITY.md`, `.github/workflows/ci.yml`.

## Implementation Hints
- Choose a compact QR implementation (e.g., minimal version/EC level auto-fit). On resource‑constrained devices, fixed version + L/M error correction may be acceptable.
- Render as a monochrome matrix using Canvas or draw primitives available in Connect IQ.
- If length exceeds capacity, fall back to JSON view and log an error.

## Inputs / Outputs
- Input: Current day’s insight packet object (already built in app memory).
- Output: On‑screen QR code representing a compact string (e.g., JSON or a compressed representation). For this task, plain JSON is acceptable.

## Error Cases
- Packet missing or serialization failure → show JSON fallback; log error.
- QR generation overflow → show JSON fallback; log warning with length.

## Timebox
- Aim to complete within 60–90 minutes with a small, reviewable diff.

## PR Checklist (must be checked in PR template)
- [ ] Scannable QR rendered; JSON fallback preserved
- [ ] No changes to score engine formulas
- [ ] Error handling added around QR encoding
- [ ] Minimal test/harness updated/added
- [ ] How‑to‑validate notes in PR description
