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
5. Do NOT modify (without explicit approval)
   - SECURITY.md, .gitignore, .github/workflows/ci.yml, or any security policies.
   - Keep existing branch protections intact; changes must go through a PR.

How to run (recommended)
- Use a dedicated branch for each run, e.g. `exp/cloudcode/<TASK>` or `micro-<TASK>-<timestamp>` for micro-issues.
- Provide the task file path (e.g., bakeoff/tasks/T-001-qr-encoder.md) in the initial instruction.
- Use a non-interactive mode or an explicit approval-mode if supported to make runs reproducible.
- For micro-issues, consider single-file implementation approach (< 300 lines).
 - Prefer isolated workspaces using git worktree to avoid clobbering: `git worktree add ../wb-cloudcode exp/cloudcode/<TASK>`

Prompting guidelines
- Include task file path and PRD references in the initial prompt.
- Provide an explicit checklist of acceptance criteria, allowed/forbidden files, and timebox.
- Require the agent to produce a PR description containing: summary, files changed, test steps, `How to validate` block, and checklist from `.github/PULL_REQUEST_TEMPLATE_BAKEOFF.md`.

Commit & PR policy
- Use branch naming: `exp/cloudcode/<TASK>-<ts>`.
- Commit message format: `feat(cloudcode): <short summary> (T-xxx)`.
- Open PR using the bakeoff PR template; include a short `How to validate` and sample test outputs.

Pre-review gates
- Run `./scripts/prepare-copilot-review.sh` before PR creation to validate:
  - Tests pass (`./scripts/run_tests.sh`)
  - Working directory is clean
  - Logger/ErrorCodes integration present where expected
  - Scope is appropriate (< 300 lines for micro-issues)
- Phase-specific validation: `./scripts/validate_phase2.sh`, `./scripts/validate_phase3.sh`
- Dashboard tests: Python tests in `dashboard/tests/` directory

GitHub Actions integration
- Existing workflows can be triggered via workflow_dispatch:
  - `simple-automation.yml`: Single-file micro-issue automation
  - `phase3-automation.yml`: Phase 3 specific automation
  - `dashboard-automation.yml`: Dashboard component automation
- Workflow inputs typically include `task_name` and `issue_number`
- Automated PR creation follows structured templates
- Issue comments track progress and include Copilot review context

Validation scripts
- Test execution: `./scripts/run_tests.sh`
- Pre-commit validation: `./scripts/precommit-guard.sh`
- Copilot review prep: `./scripts/prepare-copilot-review.sh`
- Dashboard scripts: `dashboard/scripts/` (validate_pipeline.py, etc.)
- ConnectIQ SDK setup: `./scripts/setup_connectiq_sdk.sh`

Rollback strategy
- On failure, perform comprehensive rollback:
  - Restore working directory (`git checkout -- .`)
  - Clean untracked files (`git clean -fd`)
  - Delete created branch if not main
  - Update issue with failure details and next steps
- Device API considerations: Some Garmin APIs require device/simulator
- Consider manual implementation for complex device integration

Test infrastructure
- Python tests: `dashboard/tests/` directory
- Test vectors: `dashboard/tests/test_vectors.py`
- Phase 3 tests: `dashboard/tests/phase3/` directory
- Run Python tests with: `PYTHONPATH=. python3 <test_file>`
- ConnectIQ tests may require SDK setup and device/simulator

Audit logging
- Keep a copy of the initial prompt and all major outputs in `bakeoff/artifacts/cloudcode/<TASK>-<ts>.log` for traceability. Agents should write the artifact to disk as part of the PR.
- Include workflow run logs and issue comment history for full audit trail.

Example minimal prompt snippet
```
Task: Implement T-001 (bakeoff/tasks/T-001-qr-encoder.md)
Repo root: /workdir
Allowed paths: source/**, tests/**, docs/**, bakeoff/**
Forbidden: .github/workflows/**, SECURITY.md, .env
Timebox: 90 minutes
Deliverable: PR on branch exp/cloudcode/T-001 with code, one unit test, and PR description using .github/PULL_REQUEST_TEMPLATE_BAKEOFF.md
Pre-review: Run ./scripts/prepare-copilot-review.sh before PR creation
Validation: Ensure ./scripts/run_tests.sh passes
Rubric: Address correctness vs AC, safety/tests, maintainability, performance footprint, and DevEx in PR description.
```

Micro-issue automation example
```
Task: Implement settings-menu micro-issue
Issue: #15
Scope: Single file implementation (<300 lines)
Branch: micro-settings-menu-<timestamp>
Validation: File compiles, functions correctly, tests pass
Automation: Can leverage simple-automation.yml workflow pattern
```

If Cloud Code CLI provides an SDK or command to execute code changes, prefer to run it in a sandboxed environment (worktree or fresh clone) and capture outputs in the artifact log.

Contact
- If unsure, stop and ask for human clarification referencing PRD and bakeoff tasks. Do not proceed with large refactors without human review.
