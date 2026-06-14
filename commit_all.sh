#!/bin/bash

# Switch to the project root directory (directory where this script is located)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT" || exit 1

echo "==== Current working directory: $(pwd) ===="

# 1. Check changed files
echo -e "\n[1] Checking repository status"
git status

# 2. Auto-refresh concept diagram
echo -e "\n[2] Checking for agent README changes"

if git status --porcelain -- agents/ | grep -qE '\bagents/[^/]+/[^/]+/README\.md$'; then
    echo "  Agent README changes detected. Regenerating concept diagram..."
    if python3 "$PROJECT_ROOT/diagrams/generate_concept.py"; then
        echo "  ✓ Concept diagram refreshed (diagrams/concept.svg)"
    else
        echo "  WARNING: Failed to generate concept diagram. Please check generate_concept.py" >&2
    fi
else
    echo "  No agent README changes detected. Skipping."
fi

# 3. Stage all files
echo -e "\n[3] Staging all changes"
git add .

# 4. Read commit message
read -p "Enter commit message: " commit_msg

# 5. Commit
echo -e "\n[4] Creating commit"
git commit -m "$commit_msg"

if [ $? -ne 0 ]; then
    echo "ERROR: Commit failed"
    exit 1
fi

# 6. Push current branch
CURRENT_BRANCH=$(git branch --show-current)

echo -e "\n[5] Pushing branch '$CURRENT_BRANCH' to remote"
git push origin "$CURRENT_BRANCH"

if [ $? -eq 0 ]; then
    echo "SUCCESS: Commit and push completed"
else
    echo "ERROR: Push failed"
    exit 1
fi