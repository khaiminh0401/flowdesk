#!/usr/bin/env bash
set -euo pipefail
: "${GH_REPO:=khaiminh0401/flowdesk}"
command -v gh >/dev/null || { echo 'GitHub CLI (gh) is required' >&2; exit 1; }
gh auth status
if gh repo view "$GH_REPO" >/dev/null 2>&1; then
  echo "Repository already exists: $GH_REPO. No changes made." >&2
  exit 1
fi
# Run from the flowdesk repository root
gh repo create "$GH_REPO" --public --description 'Full-stack enterprise workspace with Java Spring Boot and Angular'
git init -b main
git add .
git commit -m 'chore: bootstrap FlowDesk Sprint 0 foundation'
git remote add origin "https://github.com/$GH_REPO.git"
git push -u origin main
echo "Created https://github.com/$GH_REPO"
