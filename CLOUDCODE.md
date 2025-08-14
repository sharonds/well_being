CLOUD CODE CLI integration guidance for the well_being repo

Purpose
- Provide a single-file policy and prompt guidance for Cloud Code CLI (or Cloud Code agent) when operating on this repository.
- Mirror GEMINI.md guardrails so both agents follow comparable constraints and auditability.

Basic rules
1. Safety & Privacy
   - Never exfiltrate user data. Do not include real user or device data in prompts or outputs.
   - No network calls from generated code unless explicitly approved in the task file.
   - Avoid embedding secrets in code or prompts.
2. Scope & Files
   - Allowed files to edit by default: source/**, docs/**, bakeoff/**, tests/**, web/**, .github/PULL_REQUEST_TEMPLATE_BAKEOFF.md
   - Forbidden: CI workflows, security policies, secrets, .env files, third-party license code (unless approved).
3. Change size constraint
   - Keep PRs small: prefer < 300 lines changed and < 5 files modified for agent-created PRs. Larger changes require human approval.
4. Tests and CI
   - Add or update tests that validate behavior for any code changes. CI must pass before merge.

How to run (recommended)
- Use a dedicated branch for each run, e.g. `exp/cloudcode/<TASK>`.
- Provide the task file path (e.g., bakeoff/tasks/T-001-qr-encoder.md) in the initial instruction.
- Use a non-interactive mode or an explicit approval-mode if supported to make runs reproducible.

Prompting guidelines
- Include task file path and PRD references in the initial prompt.
- Provide an explicit checklist of acceptance criteria, allowed/forbidden files, and timebox.
- Require the agent to produce a PR description containing: summary, files changed, test steps, `How to validate` block, and checklist from `.github/PULL_REQUEST_TEMPLATE_BAKEOFF.md`.

Commit & PR policy
- Use branch naming: `exp/cloudcode/<TASK>-<ts>`.
- Commit message format: `feat(cloudcode): <short summary> (T-xxx)`.
- Open PR using the bakeoff PR template; include a short `How to validate` and sample test outputs.

Audit logging
- Keep a copy of the initial prompt and all major outputs in `bakeoff/artifacts/cloudcode-<TASK>-<ts>.log` for traceability. Agents should write the artifact to disk as part of the PR.

Example minimal prompt snippet
```
Task: Implement T-001 (bakeoff/tasks/T-001-qr-encoder.md)
Repo root: /workdir
Allowed paths: source/**, tests/**, docs/**, bakeoff/**
Forbidden: .github/workflows/**, SECURITY.md, .env
Timebox: 90 minutes
Deliverable: PR on branch exp/cloudcode/T-001 with code, one unit test, and PR description using .github/PULL_REQUEST_TEMPLATE_BAKEOFF.md
```

If Cloud Code CLI provides an SDK or command to execute code changes, prefer to run it in a sandboxed environment (worktree or fresh clone) and capture outputs in the artifact log.

Contact
- If unsure, stop and ask for human clarification referencing PRD and bakeoff tasks. Do not proceed with large refactors without human review.
