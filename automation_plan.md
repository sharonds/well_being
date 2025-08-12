Perfect—here’s a **refreshed, streamlined flow** that bakes in the biggest wins from the latest GitHub/VS Code docs while keeping the whole thing simple and as hands-off as possible.

# One clear path: VS Code (Agent Mode) → hand off to GitHub Copilot Coding Agent → PR checks → merge

## 0) Preconditions (one-time)

* **Enable Copilot Coding Agent** at org/repo level (it’s off by default for Business/Enterprise). ([GitHub Docs][1])
* **Turn on branch protection + required status checks** so nothing merges without green CI. ([GitHub Docs][2])
* **Enable CodeQL “default setup”** so every PR is security-scanned automatically. You can advance later if needed. ([GitHub Docs][3])

## 1) Ground the scope (minimize drift)

* Put your **PRD at `/docs/PRD.md`** and open **one GitHub Issue** that links to it. In the Issue description, add:

  * “MVP only; out-of-scope list”
  * Acceptance criteria + test expectations per feature
  * “If you discover bugs or deps, log sub-tasks under this Issue; do **not** add features.”
* This is important because the Coding Agent works Issue-first and is best at well-bounded tasks. ([GitHub Docs][4])

## 2) Create the build plan once in VS Code (Agent Mode)

* In VS Code, switch to **Copilot Agent Mode** and ask it to:

  * “Break the PRD into 2–4 phases, ≤5 tasks each, each with **acceptance criteria + test plan**. Produce a task checklist back into the GitHub Issue.”
* Agent Mode is built for **multi-step planning + edits** and now supports **MCP tools** if you want it to pull structured context (optional). ([Visual Studio Code][5])

## 3) Hand off execution to the **Coding Agent** (minimal human touch)

* From the Issue, **assign to `@copilot`** (or via VS Code UI) and let the **Copilot Coding Agent** run in the background: it creates a branch, drafts commits, opens a PR, and iterates based on PR comments. You review only at the PR boundary. ([Visual Studio Code][6], [GitHub Docs][4])

## 4) Enforce quality gates automatically

* On every PR the agent opens:

  * **CI + tests** must pass (required checks). ([GitHub Docs][7])
  * **CodeQL scan** runs; the agent must address findings before merge. ([GitHub Docs][8])
* This is the simplest “autonomy with guardrails” loop: the agent iterates until checks are green. ([GitHub Docs][9])

## 5) Merge & deploy

* When CI + CodeQL are green and acceptance criteria are satisfied in the PR description, merge. (Keep the deployment step in Actions so it’s part of the same gated flow.) ([GitHub Docs][7])

## 6) Learn & loop

* Close the Issue with a short summary of: what shipped vs. PRD, evidence (tests/links), and any logged bugs for the next cycle. The Coding Agent workflow is designed around this Issue→PR cadence. ([GitHub Docs][4])

---

## Why these changes matter (major upgrades only)

1. **True autonomy where it belongs:** We plan once in VS Code, then **delegate to the Coding Agent** to work “headless” on GitHub (branches, commits, PRs) so you’re not babysitting edits locally. ([GitHub Docs][9], [Visual Studio Code][6])

2. **Scope lock + drift control:** Using a single Issue with explicit out-of-scope and “log bugs only” rules keeps the agent focused—this is how GitHub intends you to steer it. ([GitHub Docs][4])

3. **Security & quality by default:** Required checks + CodeQL default setup are the lightest-weight way to keep the agent honest without extra human steps. ([GitHub Docs][2])

4. **MCP when you need it (optional):** If your plan benefits from external tools/data (docs, issue search, telemetry), Agent Mode now supports **MCP servers**; you can later mirror that configuration for the Coding Agent. This stays optional to keep v1 simple. ([Visual Studio Code][10], [GitHub Docs][11])

---

If you’re good with this, I’ll turn it into a **single “master prompt”** you can paste into VS Code Agent Mode that: (a) structures phases/tasks from your PRD, (b) posts the checklist to the Issue, (c) sets the constraints, and (d) delegates execution to the Coding Agent automatically.

[1]: https://docs.github.com/en/copilot/concepts/coding-agent/enable-coding-agent?utm_source=chatgpt.com "About enabling Copilot coding agent"
[2]: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/managing-a-branch-protection-rule?utm_source=chatgpt.com "Managing a branch protection rule"
[3]: https://docs.github.com/code-security/secure-coding/setting-up-code-scanning-for-a-repository?utm_source=chatgpt.com "Configuring default setup for code scanning"
[4]: https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent?utm_source=chatgpt.com "Copilot coding agent"
[5]: https://code.visualstudio.com/docs/copilot/chat/chat-agent-mode?utm_source=chatgpt.com "Use agent mode in VS Code"
[6]: https://code.visualstudio.com/docs/copilot/copilot-coding-agent?utm_source=chatgpt.com "GitHub Copilot coding agent"
[7]: https://docs.github.com/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches?utm_source=chatgpt.com "About protected branches"
[8]: https://docs.github.com/code-security/code-scanning/introduction-to-code-scanning/about-code-scanning-with-codeql?utm_source=chatgpt.com "About code scanning with CodeQL"
[9]: https://docs.github.com/copilot/concepts/about-copilot-coding-agent?utm_source=chatgpt.com "About Copilot coding agent"
[10]: https://code.visualstudio.com/blogs/2025/02/24/introducing-copilot-agent-mode?utm_source=chatgpt.com "Introducing GitHub Copilot agent mode (preview)"
[11]: https://docs.github.com/copilot/how-tos/agents/copilot-coding-agent/extending-copilot-coding-agent-with-mcp?utm_source=chatgpt.com "Extending Copilot coding agent with the Model Context ..."
