# Bake-off Framework

This folder contains lightweight assets to run A/B agent experiments safely:

- `tasks/` – Single-source-of-truth task specs (e.g., T-001 QR encoder)
- `compare_prs.sh` – Tiny helper to compare two branches vs base

Workflow:
1. Create two branches: `exp/cloudcode/<TASK>` and `exp/gemini/<TASK>`.
2. Point each agent to the same task file under `tasks/`.
3. Open two PRs using `.github/PULL_REQUEST_TEMPLATE_BAKEOFF.md`.
4. Use CI + `compare_prs.sh` to evaluate; merge the winner.

Guardrails:
- Keep diffs small; no changes to PRD/score formulas unless specified.
- No network calls or unsafe dependencies. Respect repo security policies.
