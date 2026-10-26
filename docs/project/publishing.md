# Repository administration

The FlowDesk repository and M0 issues already exist. Do not rerun bootstrap publishing on this checkout. Normal contributions use a feature branch and draft PR as described in CONTRIBUTING.md; `main` is not modified directly.

Historical bootstrap scripts require GitHub CLI authentication and permissions. `publish-new-repo.sh` refuses an existing remote repository. `create-sprint0-issues.sh` refuses when FD-001 already exists, and sends JSON issue bodies directly through stdin to preserve Markdown. Its regression test uses a fake CLI and performs no network writes:

```bash
python3 -m unittest discover -s scripts/tests
```

Canonical issue drafts are in `scripts/issue-data.json` and the readable Sprint 0 issue document. Review each acceptance criterion against actual evidence; never close an issue just because a PR references it. CI must run on the actual PR commit before M0 can be considered verified.
