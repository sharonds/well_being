GEMINI integration guidance for the well_being repo

Purpose
- Provide a single-file policy and prompt guidance for Gemini CLI / Gemini IDE Companion when operating on this repository.
- Keep prompts deterministic, safe, and reviewable. Ensure generated code meets project guardrails.

Basic rules
1. Safety & Privacy
   - Never exfiltrate user data. Do not include real user or device data in prompts or outputs.
   - No network calls from generated code; all processing must be local to device or browser.
   - Avoid embedding secrets in code or prompts.
2. Scope & Files
   - Allowed files to edit by default: source/**, docs/**, bakeoff/**, tests/**, web/**, .github/PULL_REQUEST_TEMPLATE_BAKEOFF.md
   - Forbidden: CI workflows, security policies, keys, .env files, third-party license code (unless clearly marked and approved).
3. Change size constraint
   - Keep PRs small: prefer < 300 lines changed and < 5 files modified for agent-created PRs. Larger changes require human approval.
4. Tests and CI
   - Add or update tests that validate behavior for any code changes. CI must pass before merge.

How to run (recommended)
- Use a dedicated branch for each run, e.g. `exp/gemini/<TASK>`.
- Point Gemini at the repo root and specify the task file (bakeoff/tasks/T-001-qr-encoder.md).
- Use non-interactive mode for reproducibility where possible: `gemini -p "Implement T-001 per bakeoff/tasks/T-001-qr-encoder.md" --approval-mode=auto_edit`

Prompting guidelines
- Always include the task file path and the PRD references in the initial prompt.
- Start with a short, deterministic checklist (ACs) followed by allowed files and explicit forbidden edits.
- Provide test harness instructions and local validation commands.
- Require the agent to produce a PR description containing: summary, files changed, test steps, `How to validate` block, and checklist from `.github/PULL_REQUEST_TEMPLATE_BAKEOFF.md`.

Commit & PR policy
- Use branch naming: `exp/gemini/<TASK>-<ts>`.
- Commit message format: `feat(gemini): <short summary> (T-xxx)`.
- Open PR using the bakeoff PR template; include a short `How to validate` and sample test outputs.

Example minimal prompt snippet
```
Task: Implement T-001 (bakeoff/tasks/T-001-qr-encoder.md)
Repo root: /workdir
Allowed paths: source/**, tests/**, docs/**, bakeoff/**
Forbidden: .github/workflows/**, SECURITY.md, .env
Timebox: 90 minutes
Deliverable: PR on branch exp/gemini/T-001 with code, one unit test, and PR description using .github/PULL_REQUEST_TEMPLATE_BAKEOFF.md
```

Audit logging
- Keep a copy of the initial prompt and all major outputs in `bakeoff/artifacts/gemini-<TASK>-<ts>.log` for traceability. Agents should write the artifact to disk as part of the PR.

Contact
- If unsure, stop and ask for human clarification referencing PRD and bakeoff tasks. Do not proceed with large refactors without human review.
