# Garmin Well-Being MVP

Personal on-device readiness score experiment. See /docs/PRD.md and /execution_plan.md.

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

## Phase 1 Slice (Current)
Minimal watch app computing a prototype score (steps + resting HR placeholders) with manual START key refresh throttled to 5 minutes.

## Build (Planned)
Connect IQ SDK 7.2.0 (toolchain setup instructions TBD). CI will run build + unit tests + CodeQL.

### Local Build (Planned Steps)
1. Install Connect IQ SDK 7.2.0 and ensure `monkeyc` is on PATH.
2. Generate a developer key: `monkeybrains --generate-key developer_key.der` (or via SDK manager).
3. Compile: `monkeyc -o build/WellBeing.prg -f source/manifest.xml -y developer_key.der -w` (add device / product flags as needed).
4. Run in simulator: `connectiq` (open simulator and load PRG).

Placeholder artifacts exist until SDK steps are integrated.

## Automation Flow
1. Single Issue with checklist.
2. Assign to @copilot to trigger Coding Agent once scaffold & CI are in main.
3. Each PR must keep tests green and expand coverage as features land.

## CI Status (Current)
- Build: Placeholder echo steps (needs real Connect IQ build command)
- Tests: Placeholder (no harness yet)
- CodeQL: Enabled with placeholder language (JS) to activate security workflow

## Next Engineering TODOs
- Integrate real Connect IQ SDK install & compilation in ci.yml
- Choose or implement unit test framework approach
- Replace CodeQL placeholder language once/if Monkey C support emerges (retain for workflow gating)
 - Add developer key management (encrypted in repo or manual secret) for CI signing if required

## Disclaimer
Not medical advice. Personal experimentation only.
