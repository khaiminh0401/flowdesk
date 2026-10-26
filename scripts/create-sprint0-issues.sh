#!/usr/bin/env bash
set -euo pipefail
: "${GH_REPO:=khaiminh0401/flowdesk}"
if ! command -v gh >/dev/null; then echo 'Install GitHub CLI (gh) first' >&2; exit 1; fi
gh auth status >/dev/null
# Run only after the repository exists, and only once, to avoid duplicates.
if gh issue list -R "$GH_REPO" --state all --limit 200 --json title --jq '.[].title' | grep -q '^FD-001:'; then
  echo 'At least one Sprint 0 issue already exists; review issues before running.' >&2
  exit 1
fi
gh api -X POST "repos/$GH_REPO/milestones" -f title='M0 — Engineering Foundation' -f due_on='2026-11-01T23:59:59Z' -f description='Sprint 0 foundation: monorepo, bootstraps, DB, CI, architecture docs' >/dev/null
python3 - <<'PYTHON'
import json
import os
import subprocess
from pathlib import Path

for issue in json.loads(Path('scripts/issue-data.json').read_text()):
    subprocess.run([
        'gh', 'issue', 'create', '-R', os.environ.get('GH_REPO', 'khaiminh0401/flowdesk'),
        '--title', issue['title'], '--body-file', '-',
        '--milestone', 'M0 — Engineering Foundation',
    ], input=issue['body'], text=True, check=True)
PYTHON
