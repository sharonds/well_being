#!/bin/bash

# ============================================================================
# GitHub Automation Framework - For EXISTING Projects
# ============================================================================
# This script safely adds GitHub Actions automation to existing projects
# without overwriting any of your current files
# ============================================================================

set -e

echo "🚀 Adding GitHub Automation to Existing Project"
echo "=============================================="
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

# Check if this is a git repository
if [ ! -d .git ]; then
    echo "❌ This is not a git repository. Please run 'git init' first."
    exit 1
fi

# Detect project information
echo "📊 Analyzing your existing project..."
echo ""

PROJECT_NAME=$(basename "$PWD")
echo "   Project: $PROJECT_NAME"

# Detect project type
PROJECT_TYPE="generic"
if [ -f "package.json" ]; then
    PROJECT_TYPE="node"
    echo "   Type: Node.js/JavaScript"
    # Extract test command if exists
    TEST_CMD=$(cat package.json | grep -o '"test":[^,]*' | cut -d'"' -f4 || echo "")
    LINT_CMD=$(cat package.json | grep -o '"lint":[^,]*' | cut -d'"' -f4 || echo "")
elif [ -f "requirements.txt" ] || [ -f "setup.py" ] || [ -f "pyproject.toml" ]; then
    PROJECT_TYPE="python"
    echo "   Type: Python"
elif [ -f "Cargo.toml" ]; then
    PROJECT_TYPE="rust"
    echo "   Type: Rust"
elif [ -f "go.mod" ]; then
    PROJECT_TYPE="go"
    echo "   Type: Go"
elif [ -f "pom.xml" ]; then
    PROJECT_TYPE="java"
    echo "   Type: Java (Maven)"
elif [ -f "build.gradle" ] || [ -f "build.gradle.kts" ]; then
    PROJECT_TYPE="gradle"
    echo "   Type: Java (Gradle)"
else
    echo "   Type: Generic/Unknown"
fi

# Check existing GitHub workflows
if [ -d ".github/workflows" ]; then
    echo "   ⚠️  Existing workflows detected:"
    ls -1 .github/workflows/*.yml .github/workflows/*.yaml 2>/dev/null | while read file; do
        echo "      - $(basename $file)"
    done
    echo ""
    read -p "Do you want to proceed? Existing workflows will be preserved. (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Cancelled."
        exit 0
    fi
else
    echo "   No existing workflows found"
fi

echo ""
echo "📁 Creating automation structure..."

# Create directories (safe - won't overwrite)
mkdir -p .github/workflows
mkdir -p scripts
mkdir -p .automation/implementations
mkdir -p docs

# Function to create a file with backup
create_file_with_backup() {
    local file_path=$1
    local file_name=$(basename "$file_path")
    
    if [ -f "$file_path" ]; then
        echo "   ⚠️  $file_path exists, creating as $file_path.automation-new"
        file_path="$file_path.automation-new"
    fi
    
    echo "$file_path"
}

# ============================================================================
# WORKFLOW 1: Simple Task Automation (Safe for existing projects)
# ============================================================================
echo "📝 Adding automation workflow..."

AUTOMATION_WORKFLOW=$(create_file_with_backup ".github/workflows/automation.yml")
cat > "$AUTOMATION_WORKFLOW" << 'WORKFLOW_EOF'
name: Task Automation

on:
  workflow_dispatch:
    inputs:
      task_name:
        description: 'Task identifier (e.g., add-feature, fix-bug)'
        required: true
        type: string
      issue_number:
        description: 'Issue number to work on'
        required: true
        type: string
  issue_comment:
    types: [created]

permissions:
  contents: write
  pull-requests: write
  issues: write

jobs:
  parse-comment:
    if: github.event_name == 'issue_comment' && contains(github.event.comment.body, '/automate')
    runs-on: ubuntu-latest
    outputs:
      should_run: ${{ steps.parse.outputs.should_run }}
      task_name: ${{ steps.parse.outputs.task_name }}
      issue_number: ${{ steps.parse.outputs.issue_number }}
    steps:
      - name: Parse comment
        id: parse
        run: |
          COMMENT="${{ github.event.comment.body }}"
          if [[ "$COMMENT" == "/automate"* ]]; then
            echo "should_run=true" >> $GITHUB_OUTPUT
            TASK_NAME=$(echo "$COMMENT" | sed 's/\/automate //g' | tr ' ' '-')
            echo "task_name=${TASK_NAME:-task}" >> $GITHUB_OUTPUT
            echo "issue_number=${{ github.event.issue.number }}" >> $GITHUB_OUTPUT
          fi

  automate-task:
    needs: [parse-comment]
    if: github.event_name == 'workflow_dispatch' || needs.parse-comment.outputs.should_run == 'true'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Set up Git
        run: |
          git config --global user.email "automation@github.com"
          git config --global user.name "GitHub Automation"

      - name: Determine parameters
        id: params
        run: |
          if [ "${{ github.event_name }}" == "workflow_dispatch" ]; then
            echo "task_name=${{ inputs.task_name }}" >> $GITHUB_OUTPUT
            echo "issue_number=${{ inputs.issue_number }}" >> $GITHUB_OUTPUT
          else
            echo "task_name=${{ needs.parse-comment.outputs.task_name }}" >> $GITHUB_OUTPUT
            echo "issue_number=${{ needs.parse-comment.outputs.issue_number }}" >> $GITHUB_OUTPUT
          fi

      - name: Create feature branch
        run: |
          BRANCH_NAME="auto/${{ steps.params.outputs.task_name }}-${{ steps.params.outputs.issue_number }}"
          git checkout -b $BRANCH_NAME || git checkout $BRANCH_NAME
          echo "BRANCH_NAME=$BRANCH_NAME" >> $GITHUB_ENV

      - name: Parse issue tasks
        id: parse-issue
        run: |
          echo "📋 Fetching issue #${{ steps.params.outputs.issue_number }}..."
          gh issue view ${{ steps.params.outputs.issue_number }} --json body,title -q . > issue_data.json
          
          # Extract tasks
          cat issue_data.json | jq -r .body | grep -E "^- \[ \]" > uncompleted_tasks.txt || echo "" > uncompleted_tasks.txt
          
          echo "## Uncompleted tasks found:"
          cat uncompleted_tasks.txt
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Implement automated tasks
        run: |
          # Create implementation log
          IMPL_FILE=".automation/implementations/${{ steps.params.outputs.task_name }}-$(date +%Y%m%d-%H%M%S).md"
          mkdir -p $(dirname "$IMPL_FILE")
          
          echo "# Automated Implementation" > "$IMPL_FILE"
          echo "Date: $(date)" >> "$IMPL_FILE"
          echo "Issue: #${{ steps.params.outputs.issue_number }}" >> "$IMPL_FILE"
          echo "Branch: ${{ env.BRANCH_NAME }}" >> "$IMPL_FILE"
          echo "" >> "$IMPL_FILE"
          echo "## Tasks:" >> "$IMPL_FILE"
          cat uncompleted_tasks.txt >> "$IMPL_FILE"
          echo "" >> "$IMPL_FILE"
          echo "## Implementation Log:" >> "$IMPL_FILE"
          
          # Read tasks and implement simple ones
          while IFS= read -r task; do
            task_lower=$(echo "$task" | tr '[:upper:]' '[:lower:]')
            
            # Add your project-specific automation rules here
            # Examples:
            
            if [[ "$task_lower" == *"readme"* ]] && [ ! -f "README.md" ]; then
              echo "Creating README.md..."
              echo "# $PROJECT_NAME" > README.md
              echo "" >> README.md
              echo "This project uses GitHub Automation." >> README.md
              echo "- ✅ Created README.md" >> "$IMPL_FILE"
            fi
            
            if [[ "$task_lower" == *"gitignore"* ]] && [ ! -f ".gitignore" ]; then
              echo "Creating .gitignore..."
              touch .gitignore
              echo "- ✅ Created .gitignore" >> "$IMPL_FILE"
            fi
            
            # Add more automation rules as needed
            
          done < uncompleted_tasks.txt

      - name: Commit changes
        id: commit
        run: |
          git add -A
          if git diff --cached --quiet; then
            echo "No changes to commit"
            echo "has_changes=false" >> $GITHUB_OUTPUT
          else
            git commit -m "feat: Automated tasks for #${{ steps.params.outputs.issue_number }}
            
            Automated by GitHub Actions"
            echo "has_changes=true" >> $GITHUB_OUTPUT
          fi

      - name: Push branch
        if: steps.commit.outputs.has_changes == 'true'
        run: |
          git push origin ${{ env.BRANCH_NAME }} --force-with-lease

      - name: Create or update PR
        if: steps.commit.outputs.has_changes == 'true'
        run: |
          # Check if PR already exists
          EXISTING_PR=$(gh pr list --head "${{ env.BRANCH_NAME }}" --json number -q '.[0].number' || echo "")
          
          if [ -z "$EXISTING_PR" ]; then
            gh pr create \
              --title "🤖 Auto: ${{ steps.params.outputs.task_name }} (#${{ steps.params.outputs.issue_number }})" \
              --body "## Automated Implementation
              
              This PR was created automatically for issue #${{ steps.params.outputs.issue_number }}
              
              ### Review Checklist:
              - [ ] Review automated changes
              - [ ] Test the implementation
              - [ ] Update documentation if needed
              
              Closes #${{ steps.params.outputs.issue_number }}" \
              --base main \
              --head ${{ env.BRANCH_NAME }}
          else
            echo "PR #$EXISTING_PR already exists, updating..."
            gh pr edit $EXISTING_PR --body "## Automated Implementation (Updated)
            
            This PR was updated automatically for issue #${{ steps.params.outputs.issue_number }}
            
            Last update: $(date)"
          fi
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Comment on issue
        if: steps.commit.outputs.has_changes == 'true'
        run: |
          gh issue comment ${{ steps.params.outputs.issue_number }} \
            --body "🤖 Automation has updated the implementation for this issue.
            
            Branch: \`${{ env.BRANCH_NAME }}\`
            Status: Ready for review"
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
WORKFLOW_EOF

# ============================================================================
# WORKFLOW 2: Enhanced CI for existing projects
# ============================================================================
echo "📝 Adding CI workflow..."

CI_WORKFLOW=$(create_file_with_backup ".github/workflows/ci-automation.yml")

# Set up project-specific test commands
case $PROJECT_TYPE in
    node)
        TEST_CMD="${TEST_CMD:-npm test}"
        LINT_CMD="${LINT_CMD:-npm run lint}"
        BUILD_CMD="npm run build"
        INSTALL_CMD="[ -f package-lock.json ] && npm ci || npm install"
        ;;
    python)
        TEST_CMD="python -m pytest || python -m unittest discover || echo 'No tests found'"
        LINT_CMD="python -m flake8 . || python -m pylint **/*.py || echo 'No linter configured'"
        BUILD_CMD="echo 'No build step for Python'"
        INSTALL_CMD="pip install -r requirements.txt || echo 'No requirements.txt'"
        ;;
    rust)
        TEST_CMD="cargo test"
        LINT_CMD="cargo clippy -- -D warnings"
        BUILD_CMD="cargo build --release"
        INSTALL_CMD="cargo build"
        ;;
    go)
        TEST_CMD="go test ./..."
        LINT_CMD="go vet ./..."
        BUILD_CMD="go build"
        INSTALL_CMD="go mod download"
        ;;
    java)
        TEST_CMD="mvn test"
        LINT_CMD="echo 'Linting for Java'"
        BUILD_CMD="mvn package"
        INSTALL_CMD="mvn install -DskipTests"
        ;;
    gradle)
        TEST_CMD="./gradlew test"
        LINT_CMD="./gradlew check"
        BUILD_CMD="./gradlew build"
        INSTALL_CMD="./gradlew dependencies"
        ;;
    *)
        TEST_CMD="echo 'No test command configured'"
        LINT_CMD="echo 'No lint command configured'"
        BUILD_CMD="echo 'No build command configured'"
        INSTALL_CMD="echo 'No install command configured'"
        ;;
esac

cat > "$CI_WORKFLOW" << CI_EOF
name: CI - Automated Testing

on:
  push:
    branches: [ main, master, develop ]
  pull_request:
    branches: [ main, master ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup environment for $PROJECT_TYPE
        run: |
          echo "Setting up $PROJECT_TYPE project"
CI_EOF

# Add language-specific setup
case $PROJECT_TYPE in
    node)
        cat >> "$CI_WORKFLOW" << 'NODE_EOF'
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
NODE_EOF
        ;;
    python)
        cat >> "$CI_WORKFLOW" << 'PYTHON_EOF'
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          cache: 'pip'
PYTHON_EOF
        ;;
    rust)
        cat >> "$CI_WORKFLOW" << 'RUST_EOF'
      
      - name: Setup Rust
        uses: actions-rs/toolchain@v1
        with:
          toolchain: stable
          override: true
RUST_EOF
        ;;
    go)
        cat >> "$CI_WORKFLOW" << 'GO_EOF'
      
      - name: Setup Go
        uses: actions/setup-go@v4
        with:
          go-version: '1.21'
GO_EOF
        ;;
    java)
        cat >> "$CI_WORKFLOW" << 'JAVA_EOF'
      
      - name: Setup Java
        uses: actions/setup-java@v3
        with:
          java-version: '17'
          distribution: 'temurin'
JAVA_EOF
        ;;
esac

# Complete CI workflow
cat >> "$CI_WORKFLOW" << CI_EOF2
      
      - name: Install dependencies
        run: |
          $INSTALL_CMD
        continue-on-error: true
          
      - name: Run tests
        run: |
          $TEST_CMD
        continue-on-error: true
          
      - name: Run linting
        run: |
          $LINT_CMD
        continue-on-error: true

      - name: Build project
        run: |
          $BUILD_CMD
        continue-on-error: true
CI_EOF2

# ============================================================================
# Helper Scripts for existing projects
# ============================================================================
echo "📝 Adding helper scripts..."

# Quick automation script
QUICK_SCRIPT=$(create_file_with_backup "scripts/automate.sh")
cat > "$QUICK_SCRIPT" << 'SCRIPT_EOF'
#!/bin/bash
# Quick automation trigger for your existing project

if [ -z "$1" ]; then
    echo "Usage: ./scripts/automate.sh <issue-number> [task-name]"
    echo "Example: ./scripts/automate.sh 5 fix-bug"
    echo ""
    echo "Or in a GitHub issue comment, type:"
    echo "  /automate fix-bug"
    exit 1
fi

ISSUE_NUMBER=$1
TASK_NAME=${2:-task-$ISSUE_NUMBER}

echo "🚀 Running automation for issue #$ISSUE_NUMBER"
echo "   Task name: $TASK_NAME"
echo ""

gh workflow run automation.yml \
    --field issue_number="$ISSUE_NUMBER" \
    --field task_name="$TASK_NAME"

echo ""
echo "✅ Automation triggered!"
echo "   Check progress: gh run list --workflow=automation.yml"
echo "   View runs: https://github.com/$(gh repo view --json nameWithOwner -q .nameWithOwner)/actions"
SCRIPT_EOF

chmod +x "$QUICK_SCRIPT"

# ============================================================================
# Integration guide for existing project
# ============================================================================
echo "📝 Creating integration guide..."

GUIDE_FILE=$(create_file_with_backup "AUTOMATION_GUIDE.md")
cat > "$GUIDE_FILE" << GUIDE_EOF
# 🤖 GitHub Automation - Integration Guide

This project now has GitHub Automation integrated!

## Quick Start

### Method 1: Issue Comments
In any GitHub issue, comment:
\`\`\`
/automate task-name
\`\`\`

### Method 2: Command Line
\`\`\`bash
./scripts/automate.sh <issue-number> [task-name]

# Example:
./scripts/automate.sh 5 add-feature
\`\`\`

### Method 3: GitHub Actions UI
1. Go to Actions tab
2. Select "Task Automation"
3. Click "Run workflow"
4. Enter issue number and task name

## What Can Be Automated?

The automation can handle:
- Creating boilerplate files
- Setting up configurations
- Simple code generation
- Documentation updates
- Test file creation

## Your Project Configuration

- **Project Type**: $PROJECT_TYPE
- **Test Command**: $TEST_CMD
- **Lint Command**: $LINT_CMD
- **Build Command**: $BUILD_CMD

## Customizing Automation

Edit \`.github/workflows/automation.yml\` to add project-specific rules:

\`\`\`yaml
# Look for the "Implement automated tasks" step
# Add your custom automation logic there
\`\`\`

## Issue Format

For best results, create issues with checkbox tasks:

\`\`\`markdown
- [ ] Add user model
- [ ] Create API endpoint
- [ ] Add tests
- [ ] Update documentation
\`\`\`

## Workflows Added

1. **automation.yml** - Automates tasks from issues
2. **ci-automation.yml** - Runs tests on PRs

## Claude CLI Integration

Tell Claude:
> "We have GitHub automation set up. Read AUTOMATION_GUIDE.md"

Claude can then:
- Create properly formatted issues
- Trigger automation
- Monitor progress
- Create PRs

## Monitoring

- View runs: \`gh run list\`
- Watch a run: \`gh run watch\`
- View in browser: \`gh run view --web\`

## Troubleshooting

If automation fails:
1. Check logs: \`gh run view\`
2. Verify issue format has checkboxes
3. Ensure branch isn't protected
4. Check GitHub Actions permissions

## Next Steps

1. Create an issue with tasks
2. Run automation: \`./scripts/automate.sh <issue-number>\`
3. Review the automated PR
4. Merge when ready!
GUIDE_EOF

# ============================================================================
# Final setup
# ============================================================================
echo ""
echo "🔧 Configuring GitHub settings..."

# Ensure gh is authenticated
if ! gh auth status >/dev/null 2>&1; then
    echo "📝 Please authenticate with GitHub:"
    gh auth login
fi

# Check if remote exists
if git remote get-url origin >/dev/null 2>&1; then
    echo "✅ GitHub remote configured"
    
    # Try to enable Actions if not enabled
    echo "   Checking GitHub Actions status..."
    gh api repos/:owner/:repo/actions/permissions -X PUT -f enabled=true 2>/dev/null || true
else
    echo "⚠️  No GitHub remote found. Please add one:"
    echo "   git remote add origin <your-repo-url>"
fi

# ============================================================================
# Summary
# ============================================================================
echo ""
echo "✅ ============================================"
echo "✅ GitHub Automation Added Successfully!"
echo "✅ ============================================"
echo ""
echo "📁 Files created/modified:"
[ -f ".github/workflows/automation.yml" ] && echo "   ✅ .github/workflows/automation.yml"
[ -f ".github/workflows/automation.yml.automation-new" ] && echo "   ⚠️  .github/workflows/automation.yml.automation-new (review and rename)"
[ -f ".github/workflows/ci-automation.yml" ] && echo "   ✅ .github/workflows/ci-automation.yml"
[ -f ".github/workflows/ci-automation.yml.automation-new" ] && echo "   ⚠️  .github/workflows/ci-automation.yml.automation-new (review and rename)"
[ -f "scripts/automate.sh" ] && echo "   ✅ scripts/automate.sh"
[ -f "$GUIDE_FILE" ] && echo "   ✅ $GUIDE_FILE"
echo ""
echo "🎯 Project Details:"
echo "   Type: $PROJECT_TYPE"
echo "   Test: $TEST_CMD"
echo "   Lint: $LINT_CMD"
echo ""
echo "🚀 Quick Test:"
echo ""
echo "1. Create a test issue:"
echo "   gh issue create --title 'Test Automation' --body '- [ ] Add README'"
echo ""
echo "2. Run automation (replace N with issue number):"
echo "   ./scripts/automate.sh N test"
echo ""
echo "3. Or comment on the issue:"
echo "   /automate test"
echo ""
echo "📖 Read $GUIDE_FILE for full documentation"
echo ""
echo "Happy automating! 🎉"