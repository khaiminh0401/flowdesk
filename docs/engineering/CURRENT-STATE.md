# Current state / resume here

Snapshot: 2026-10-26. Repository handoff only; not automatically synchronized with GitHub. Fetch refs, read linked issues/PRs and inspect working tree/CI before continuing.

## Active milestone and base

M0 — Engineering Foundation. Baseline main `9d723b7` merged PR [#7](https://github.com/khaiminh0401/flowdesk/pull/7), including `920cce6` loopback-startup documentation. Main [CI 40293194920](https://github.com/khaiminh0401/flowdesk/actions/runs/40293194920) succeeded. Existing M0 #1–#6 remain open; no automatic issue acceptance/closure was performed.

## Verified baseline

Boot info/health, PostgreSQL/FlywayV1, strict standalone/lazy Angular shell, 2 backend unit + 7 real-PostgreSQL IT, 4 baseline Chrome tests, CI and startup documentation. No authentication, refresh/session code, workspace RBAC, business entities/transactions or Sprint 1 specification exists at this base.

## Current work

Branch `feat/FD-008-project-brain-api-connectivity`, based directly on merged main. [FD-007 #8](https://github.com/khaiminh0401/flowdesk/issues/8): persistent knowledge entry point. [FD-008 #9](https://github.com/khaiminh0401/flowdesk/issues/9): read-only dashboard/API connection, typed contract, loading/error/retry/cancellation, same-origin dev proxy and live Playwright evidence. PR/verification results are updated before delivery; never inherit main's CI status for this branch.

## Findings, failures and decisions

- Dependabot alerts request returned403 (disabled/scope). Backend CVE status is not verified. No security settings/scopes were changed.
- Hibernate has no entity mappings; direct PostgreSQL tests verify V1. No dummy entities/migrations added.
- M1 security/session policy is undefined and requires human-reviewed ADR/threat model before implementation.
- New HTTP service tests initially lacked the zoneless testing provider; that was a test-environment error, corrected to match the production bootstrap. New behavior tests run against real components/services and an isolated HTTP transport.
- Local `.env` remains ignored, configured for this checkout's loopback DB port55432. Do not print or commit its credentials; do not reset an existing DB casually.

## Next task and resume order

After this PR's acceptance, start [FD-009 #10](https://github.com/khaiminh0401/flowdesk/issues/10): write concrete identity/session contract, threat model and proposed ADR for human review. Login/session implementation #11 depends on that review, workspace #12 depends on the merged identity slice. M2+ are planning epics, not completed features.

Read [PROJECT-INTELLIGENCE](PROJECT-INTELLIGENCE.md), [PRODUCT-ROADMAP](PRODUCT-ROADMAP.md), [SECURITY-MODEL](SECURITY-MODEL.md) and [TEST-STRATEGY](TEST-STRATEGY.md). Preserve user changes and fetch actual remote state. Never merge, force-push, assume unmerged dependencies are on main, or change security policy without review.
