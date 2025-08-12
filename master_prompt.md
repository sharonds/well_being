Here’s our plan:

We have a clear MVP defined in `/docs/PRD.md`. Please read it and help me execute it with minimal human intervention—using GitHub Copilot Agent Mode coupled with the GitHub Copilot Coding Agent.

**Phase & Task Breakdown**

1. Break the PRD into 2–4 sequential phases, each with no more than 5 tasks.
2. For each task, include:
   - A brief title
   - Clear acceptance criteria
   - A concise test plan

Post the task checklist directly into the linked GitHub Issue as a checklist.

**Scope Control**

- Strictly adhere to MVP—explicitly ignore any features listed as out-of-scope in the PRD or Issue.
- If you detect bugs or dependencies, log them under a “Bugs / To-do” section in the Issue checklist, not as new features.

**Task Execution Strategy**

For each task:
1. Generate a micro-plan that includes:
   - Files/functions to create or modify
   - Steps for implementation
   - Tests to add or update
2. Execute the micro-plan locally (making edits, running toolsets/tasks).
3. Run tests automatically—if failures occur, attempt to fix; iterate until all tests pass (`autoFix` behavior).
4. When ready, do *not commit locally*. Instead, assign the GitHub Issue to `@copilot` to trigger the GitHub Copilot Coding Agent.

**Guardrails & Quality Gates**

- Ensure GitHub Actions builds/tests, and CodeQL scans must pass before PRs can be merged.
- The Coding Agent should respond to CI issues and security findings automatically, opening PR iterations as needed.

**PR & Deployment**

Once all tasks in a phase are complete and all checks are green:
- The Coding Agent should open a PR linking the PRD and Issue, summarizing acceptance criteria, tests, and results.
- Merge only after CI and security scans pass.
- Post-deploy, close the Issue with a summary of what shipped vs. PRD, test coverage, and any remaining bugs.

Let’s start with the task breakdown based on the PRD.
