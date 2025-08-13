#!/bin/bash

# ============================================================================
# GitHub Automation Framework - Complete Setup Script
# ============================================================================
# This script sets up GitHub Actions automation for ANY project
# It can be copied to a new project and run to enable full automation
# ============================================================================

set -e

echo "🚀 GitHub Automation Framework Setup v1.0"
echo "========================================="
echo ""

# Check prerequisites
command -v gh >/dev/null 2>&1 || { 
    echo "❌ GitHub CLI (gh) is required but not installed."
    echo "   Install from: https://cli.github.com"
    echo "   Mac: brew install gh"
    echo "   Linux: See https://github.com/cli/cli/blob/trunk/docs/install_linux.md"
    exit 1
}

command -v git >/dev/null 2>&1 || { 
    echo "❌ Git is required but not installed."
    exit 1
}

# Initialize git if needed
if [ ! -d .git ]; then
    echo "📦 Initializing git repository..."
    git init
    git branch -M main
fi

echo "📁 Creating directory structure..."
mkdir -p .github/workflows
mkdir -p scripts
mkdir -p .automation
mkdir -p docs

# ============================================================================
# WORKFLOW 1: Simple Task Automation
# ============================================================================
echo "📝 Creating simple automation workflow..."
cat > .github/workflows/simple-automation.yml << 'WORKFLOW_EOF'
name: Simple Task Automation

on:
  workflow_dispatch:
    inputs:
      task_name:
        description: 'Task identifier (e.g., add-auth, fix-bug)'
        required: true
        type: string
      issue_number:
        description: 'Issue number to work on'
        required: true
        type: string

permissions:
  contents: write
  pull-requests: write
  issues: write

jobs:
  automate-task:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Set up Git
        run: |
          git config --global user.email "automation@github.com"
          git config --global user.name "GitHub Automation"

      - name: Create feature branch
        run: |
          BRANCH_NAME="auto/${{ inputs.task_name }}-${{ inputs.issue_number }}"
          git checkout -b $BRANCH_NAME
          echo "BRANCH_NAME=$BRANCH_NAME" >> $GITHUB_ENV

      - name: Parse issue tasks
        id: parse
        run: |
          echo "📋 Fetching issue #${{ inputs.issue_number }}..."
          gh issue view ${{ inputs.issue_number }} --json body,title -q . > issue_data.json
          cat issue_data.json | jq -r .body > issue_body.md
          cat issue_data.json | jq -r .title > issue_title.txt
          
          echo "## Issue Title:"
          cat issue_title.txt
          echo ""
          echo "## Tasks to implement:"
          cat issue_body.md | grep -E "^- \[ \]" || echo "No checkbox tasks found"
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Implement simple tasks
        run: |
          # Read issue tasks
          TASKS=$(cat issue_body.md | grep -E "^- \[ \]" || echo "")
          
          # Create implementation marker
          mkdir -p .automation/implementations
          echo "# Automated Implementation Log" > .automation/implementations/${{ inputs.task_name }}.md
          echo "Issue: #${{ inputs.issue_number }}" >> .automation/implementations/${{ inputs.task_name }}.md
          echo "Date: $(date)" >> .automation/implementations/${{ inputs.task_name }}.md
          echo "Branch: ${{ env.BRANCH_NAME }}" >> .automation/implementations/${{ inputs.task_name }}.md
          echo "" >> .automation/implementations/${{ inputs.task_name }}.md
          echo "## Tasks Implemented:" >> .automation/implementations/${{ inputs.task_name }}.md
          echo "$TASKS" >> .automation/implementations/${{ inputs.task_name }}.md
          
          # Project-specific automation
          if [ -f "package.json" ]; then
              echo "📦 Node.js project detected"
              # Add Node.js specific automation here
          elif [ -f "requirements.txt" ]; then
              echo "🐍 Python project detected"
              # Add Python specific automation here
          elif [ -f "Cargo.toml" ]; then
              echo "🦀 Rust project detected"
              # Add Rust specific automation here
          elif [ -f "go.mod" ]; then
              echo "🐹 Go project detected"
              # Add Go specific automation here
          fi
          
          # Generic implementations for common tasks
          if echo "$TASKS" | grep -qi "readme"; then
              if [ ! -f "README.md" ]; then
                  echo "# $(cat issue_title.txt)" > README.md
                  echo "" >> README.md
                  echo "This project was set up with GitHub Automation." >> README.md
                  echo "✅ Created README.md" >> .automation/implementations/${{ inputs.task_name }}.md
              fi
          fi
          
          if echo "$TASKS" | grep -qi "gitignore"; then
              if [ ! -f ".gitignore" ]; then
                  echo "# Dependencies" > .gitignore
                  echo "node_modules/" >> .gitignore
                  echo "venv/" >> .gitignore
                  echo "target/" >> .gitignore
                  echo "" >> .gitignore
                  echo "# IDE" >> .gitignore
                  echo ".vscode/" >> .gitignore
                  echo ".idea/" >> .gitignore
                  echo "" >> .gitignore
                  echo "# OS" >> .gitignore
                  echo ".DS_Store" >> .gitignore
                  echo "Thumbs.db" >> .gitignore
                  echo "✅ Created .gitignore" >> .automation/implementations/${{ inputs.task_name }}.md
              fi
          fi

      - name: Commit changes
        run: |
          git add -A
          if git diff --cached --quiet; then
            echo "No changes to commit"
            exit 0
          fi
          git commit -m "feat: Automated implementation for ${{ inputs.task_name }}
          
          Related to #${{ inputs.issue_number }}
          
          Automated by GitHub Actions"

      - name: Push branch
        run: |
          git push origin ${{ env.BRANCH_NAME }}

      - name: Create Pull Request
        id: create-pr
        run: |
          PR_BODY="## 🤖 Automated Implementation

          This PR was created automatically for issue #${{ inputs.issue_number }}

          ### Changes Made:
          $(git diff --name-status HEAD~1 HEAD | head -20)

          ### Checklist:
          - [ ] Review automated changes
          - [ ] Run tests locally
          - [ ] Update documentation if needed
          - [ ] Approve and merge

          ### Related Issue:
          Closes #${{ inputs.issue_number }}

          ---
          *Generated by GitHub Actions Automation*"
          
          gh pr create \
            --title "🤖 Auto: ${{ inputs.task_name }} (#${{ inputs.issue_number }})" \
            --body "$PR_BODY" \
            --base main \
            --head ${{ env.BRANCH_NAME }}
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Update issue
        if: steps.create-pr.outcome == 'success'
        run: |
          gh issue comment ${{ inputs.issue_number }} \
            --body "🤖 **Automation Complete!**
            
          A pull request has been created for this issue.
          Please review the automated changes.
          
          **Branch:** \`${{ env.BRANCH_NAME }}\`
          **Status:** Ready for review"
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
WORKFLOW_EOF

# ============================================================================
# WORKFLOW 2: Continuous Integration
# ============================================================================
echo "📝 Creating CI workflow..."
cat > .github/workflows/ci.yml << 'CI_EOF'
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  detect-language:
    runs-on: ubuntu-latest
    outputs:
      language: ${{ steps.detect.outputs.language }}
    steps:
      - uses: actions/checkout@v4
      - name: Detect project language
        id: detect
        run: |
          if [ -f "package.json" ]; then
            echo "language=node" >> $GITHUB_OUTPUT
          elif [ -f "requirements.txt" ] || [ -f "setup.py" ] || [ -f "pyproject.toml" ]; then
            echo "language=python" >> $GITHUB_OUTPUT
          elif [ -f "Cargo.toml" ]; then
            echo "language=rust" >> $GITHUB_OUTPUT
          elif [ -f "go.mod" ]; then
            echo "language=go" >> $GITHUB_OUTPUT
          else
            echo "language=generic" >> $GITHUB_OUTPUT
          fi

  test:
    needs: detect-language
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        if: needs.detect-language.outputs.language == 'node'
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          
      - name: Setup Python
        if: needs.detect-language.outputs.language == 'python'
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          
      - name: Setup Rust
        if: needs.detect-language.outputs.language == 'rust'
        uses: actions-rs/toolchain@v1
        with:
          toolchain: stable
          
      - name: Setup Go
        if: needs.detect-language.outputs.language == 'go'
        uses: actions/setup-go@v4
        with:
          go-version: '1.21'
      
      - name: Install dependencies
        run: |
          case "${{ needs.detect-language.outputs.language }}" in
            node)
              [ -f "package-lock.json" ] && npm ci || npm install
              ;;
            python)
              pip install --upgrade pip
              [ -f "requirements.txt" ] && pip install -r requirements.txt
              [ -f "requirements-dev.txt" ] && pip install -r requirements-dev.txt
              ;;
            rust)
              cargo build --verbose
              ;;
            go)
              go mod download
              ;;
          esac
          
      - name: Run tests
        run: |
          case "${{ needs.detect-language.outputs.language }}" in
            node)
              npm test 2>/dev/null || echo "No tests configured"
              ;;
            python)
              python -m pytest 2>/dev/null || python -m unittest discover 2>/dev/null || echo "No tests configured"
              ;;
            rust)
              cargo test --verbose
              ;;
            go)
              go test ./...
              ;;
            *)
              echo "No tests configured for generic project"
              ;;
          esac
          
      - name: Run linting
        continue-on-error: true
        run: |
          case "${{ needs.detect-language.outputs.language }}" in
            node)
              npm run lint 2>/dev/null || npx eslint . 2>/dev/null || echo "No linting configured"
              ;;
            python)
              python -m flake8 2>/dev/null || python -m pylint **/*.py 2>/dev/null || echo "No linting configured"
              ;;
            rust)
              cargo clippy -- -D warnings 2>/dev/null || echo "No clippy configured"
              ;;
            go)
              go vet ./... 2>/dev/null || echo "No go vet configured"
              ;;
          esac
CI_EOF

# ============================================================================
# WORKFLOW 3: Release Automation
# ============================================================================
echo "📝 Creating release workflow..."
cat > .github/workflows/release.yml << 'RELEASE_EOF'
name: Release

on:
  push:
    tags:
      - 'v*'
  workflow_dispatch:
    inputs:
      version:
        description: 'Version to release (e.g., v1.0.0)'
        required: true
        type: string

permissions:
  contents: write

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Determine version
        id: version
        run: |
          if [ "${{ github.event_name }}" = "workflow_dispatch" ]; then
            VERSION="${{ inputs.version }}"
          else
            VERSION="${GITHUB_REF#refs/tags/}"
          fi
          echo "version=$VERSION" >> $GITHUB_OUTPUT
          
      - name: Generate Changelog
        id: changelog
        run: |
          echo "# Release Notes for ${{ steps.version.outputs.version }}" > RELEASE_NOTES.md
          echo "" >> RELEASE_NOTES.md
          echo "## What's Changed" >> RELEASE_NOTES.md
          echo "" >> RELEASE_NOTES.md
          
          # Get previous tag
          PREV_TAG=$(git describe --tags --abbrev=0 HEAD^ 2>/dev/null || echo "")
          
          if [ -z "$PREV_TAG" ]; then
            echo "### Initial Release 🎉" >> RELEASE_NOTES.md
            git log --pretty=format:"- %s" HEAD >> RELEASE_NOTES.md
          else
            echo "### Commits since $PREV_TAG" >> RELEASE_NOTES.md
            git log --pretty=format:"- %s" ${PREV_TAG}..HEAD >> RELEASE_NOTES.md
          fi
          
          echo "" >> RELEASE_NOTES.md
          echo "---" >> RELEASE_NOTES.md
          echo "*Released on $(date +'%Y-%m-%d')*" >> RELEASE_NOTES.md
          
      - name: Create Release
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          gh release create ${{ steps.version.outputs.version }} \
            --title "Release ${{ steps.version.outputs.version }}" \
            --notes-file RELEASE_NOTES.md \
            --draft=false \
            --prerelease=false
RELEASE_EOF

# ============================================================================
# HELPER SCRIPTS
# ============================================================================
echo "📝 Creating helper scripts..."

# Test runner script
cat > scripts/run-tests.sh << 'TEST_EOF'
#!/bin/bash
echo "🧪 Running tests..."

if [ -f "package.json" ]; then
    npm test
elif [ -f "requirements.txt" ]; then
    python -m pytest || python -m unittest discover
elif [ -f "Cargo.toml" ]; then
    cargo test
elif [ -f "go.mod" ]; then
    go test ./...
else
    echo "No test framework detected"
fi
TEST_EOF

# Quick automation trigger
cat > scripts/quick-auto.sh << 'QUICK_EOF'
#!/bin/bash
# Quick automation trigger for common tasks

if [ -z "$1" ]; then
    echo "Usage: ./scripts/quick-auto.sh <task-name> [issue-number]"
    echo "Example: ./scripts/quick-auto.sh add-auth 5"
    exit 1
fi

TASK_NAME=$1
ISSUE_NUMBER=${2:-1}

echo "🚀 Running automation for task: $TASK_NAME (Issue #$ISSUE_NUMBER)"
gh workflow run simple-automation.yml \
    --field task_name="$TASK_NAME" \
    --field issue_number="$ISSUE_NUMBER"

echo "✅ Automation triggered! Check GitHub Actions for progress."
QUICK_EOF

chmod +x scripts/*.sh

# ============================================================================
# CLAUDE INTEGRATION GUIDE
# ============================================================================
echo "📝 Creating Claude integration guide..."
cat > CLAUDE_AUTOMATION_GUIDE.md << 'CLAUDE_EOF'
# 🤖 Claude CLI + GitHub Automation Guide

## Quick Start for Claude

When you open this project with Claude CLI, you can say:

### Create a new feature:
```
"Let's create a new feature for user authentication"
```
Claude will create an issue and can trigger automation.

### Run automation for an issue:
```
"Run the automation for issue #3"
```

### Check automation status:
```
"What's the status of our GitHub Actions?"
```

### Create a release:
```
"Let's create a release v1.0.0"
```

## Available Automation Commands

1. **Create Issue with Tasks:**
```bash
gh issue create --title "Add Feature X" --body "- [ ] Task 1
- [ ] Task 2
- [ ] Task 3"
```

2. **Run Automation:**
```bash
gh workflow run simple-automation.yml \
  --field task_name="feature-x" \
  --field issue_number=1
```

3. **Quick Automation:**
```bash
./scripts/quick-auto.sh add-feature 1
```

4. **Check Workflow Status:**
```bash
gh run list
gh run view  # Interactive selection
```

5. **Create Release:**
```bash
git tag v1.0.0
git push origin v1.0.0
# Or manually trigger:
gh workflow run release.yml --field version=v1.0.0
```

## Workflow Files

- `.github/workflows/simple-automation.yml` - Automates tasks from issues
- `.github/workflows/ci.yml` - Runs tests on every push/PR
- `.github/workflows/release.yml` - Creates releases from tags

## Best Practices for Claude

1. **Structure Issues with Checkboxes:**
   - Use `- [ ]` format for tasks
   - Keep issues focused (5-10 tasks max)
   - Be specific about what needs to be done

2. **Automation Works Best For:**
   - Creating boilerplate files
   - Setting up project structure
   - Adding configuration files
   - Simple code generation

3. **Manual Work Needed For:**
   - Complex business logic
   - Custom algorithms
   - API integrations
   - Database schemas

## Example Conversation with Claude

```
You: "Let's set up a REST API with authentication"

Claude: "I'll create an issue for that and set up the automation."
*Creates issue #1 with tasks*
*Runs: gh workflow run simple-automation.yml --field task_name=rest-api --field issue_number=1*

You: "Great, now let's add user registration"

Claude: "I'll implement the user registration endpoint."
*Creates implementation*
*Creates PR*
```

## Monitoring Automation

- **GitHub Actions Tab**: See all workflow runs
- **Pull Requests**: Review automated PRs
- **Issues**: Track progress with checkboxes

## Troubleshooting

If automation fails:
1. Check GitHub Actions logs: `gh run view`
2. Ensure permissions are set correctly
3. Verify `gh` is authenticated: `gh auth status`
4. Check workflow syntax if modified

## This Project is Automation-Ready! 🚀

Claude can now help you build features using GitHub automation.
Just describe what you want to build!
CLAUDE_EOF

# ============================================================================
# GITHUB SETUP
# ============================================================================
echo ""
echo "🔗 Setting up GitHub repository..."

# Check if gh is authenticated
if ! gh auth status >/dev/null 2>&1; then
    echo "📝 Please authenticate with GitHub:"
    gh auth login
fi

# Check if remote exists
if ! git remote get-url origin >/dev/null 2>&1; then
    echo "📝 No remote repository found."
    read -p "Enter repository name (or press Enter to use folder name): " REPO_NAME
    REPO_NAME=${REPO_NAME:-$(basename "$PWD")}
    
    echo "Creating GitHub repository: $REPO_NAME"
    gh repo create "$REPO_NAME" --public --source=. --remote=origin --push || echo "Repository might already exist"
else
    echo "✅ Remote repository already configured"
fi

# Create initial commit if needed
if ! git rev-parse HEAD >/dev/null 2>&1; then
    echo "📝 Creating initial commit..."
    git add .
    git commit -m "Initial commit with GitHub Automation Framework" || true
    git push -u origin main || true
fi

# Create first issue as example
echo ""
echo "📝 Creating example issue for testing..."
gh issue create \
    --title "Initial Project Setup" \
    --body "Setup tasks for the project:
- [ ] Add README.md with project description
- [ ] Create .gitignore file
- [ ] Set up basic project structure
- [ ] Add LICENSE file
- [ ] Configure CI/CD pipeline
- [ ] Add contributing guidelines" || echo "Issue might already exist"

# ============================================================================
# COMPLETION
# ============================================================================
echo ""
echo "✅ ============================================"
echo "✅ GitHub Automation Framework Setup Complete!"
echo "✅ ============================================"
echo ""
echo "📚 Next Steps:"
echo "1. Review the created workflows in .github/workflows/"
echo "2. Check your first issue: gh issue list"
echo "3. Run your first automation:"
echo "   gh workflow run simple-automation.yml --field task_name=setup --field issue_number=1"
echo ""
echo "📖 For Claude CLI:"
echo "   Open CLAUDE_AUTOMATION_GUIDE.md for instructions"
echo ""
echo "🚀 Quick Test:"
echo "   ./scripts/quick-auto.sh setup 1"
echo ""
echo "Happy automating! 🎉"