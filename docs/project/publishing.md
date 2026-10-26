# Publishing Sprint 0

These commands require a GitHub token with permission to create public repositories and manage issues/milestones. Run them **only** from a new FlowDesk working directory; scripts refuse an existing `flowdesk` repository to protect previous work.

```bash
# From extracted flowdesk/ folder
cd apps/web && npm install && cd ../..
# Commit apps/web/package-lock.json as part of the initial commit
bash scripts/publish-new-repo.sh
bash scripts/create-sprint0-issues.sh
```

**Note:** `gh repo create` and issues/milestones scripts require authentication (`gh auth login`) and proper scopes. Do not run scripts against an existing repository without reviewing them.

Validate CI on GitHub after pushing; the initial starter was not fully executable-tested in the offline packaging environment. For reproducible installs, replace CI's `npm install` with `npm ci` once the lockfile is committed.
