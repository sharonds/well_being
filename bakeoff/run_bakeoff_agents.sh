#!/usr/bin/env bash
# Helper to run both agents locally (manual steps required for auth)
# Usage: bakeoff/run_bakeoff_agents.sh T-001

set -euo pipefail
TASK=${1:-T-001}

GEMINI_BRANCH=exp/gemini/${TASK}
CLOUDCODE_BRANCH=exp/cloudcode/${TASK}

echo "Ensure you have authenticated CLI tools and open a new terminal where VS Code companion is active."

echo "=== Gemini: start ==="
# Example: run Gemini non-interactively with a pinned prompt (user should modify)
read -p "Continue with Gemini run? (y/N) " ok
if [[ "$ok" == "y" || "$ok" == "Y" ]]; then
  gemini -p "Implement ${TASK} per bakeoff/tasks/${TASK-qr-encoder.md} on branch ${GEMINI_BRANCH}. Use GEMINI.md rules." --approval-mode=auto_edit
else
  echo "Skipping Gemini run"
fi

echo "=== Cloud Code: start ==="
read -p "Continue with Cloud Code run? (y/N) " ok
if [[ "$ok" == "y" || "$ok" == "Y" ]]; then
  echo "Run your Cloud Code CLI here with equivalent prompt and branch ${CLOUDCODE_BRANCH}."
  echo "Example (manual): cloudcode run --prompt-file bakeoff/tasks/${TASK}-qr-encoder.md --branch ${CLOUDCODE_BRANCH}"
else
  echo "Skipping Cloud Code run"
fi

echo "Done. Inspect branches and open PRs using .github/PULL_REQUEST_TEMPLATE_BAKEOFF.md"
