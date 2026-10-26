# Current state / resume here

Snapshot: 2026-10-26. Manual repository handoff, not synchronized automatically with GitHub. Fetch refs/read actual issues/PRs/CI before continuing.

## Base and active task

Main `69ad007` merged [PR #18](https://github.com/khaiminh0401/flowdesk/pull/18). Main [CI40338793703](https://github.com/khaiminh0401/flowdesk/actions/runs/40338793703) succeeded. Foundation + live dashboard connectivity are implemented: 2 API unit +7 PostgreSQL IT,18 Angular tests,4 live Playwright scenarios. No authentication, credentials model, refresh/session/RBAC or workspace domain exists.

Active M1 **design**, [FD-009/#10](https://github.com/khaiminh0401/flowdesk/issues/10), branch `docs/FD-009-identity-session-design` directly from merged main. No user changes were present at start. #1–#6/#8/#9 remain operationally open; no issue was closed or progress inflated. Earlier PR18 draft/WIP snapshot is superseded by this actual merge discovery.

## Reviewable proposal

- [ADR-0002](../adr/0002-identity-session-lifecycle.md): **Proposed**, no approval recorded. Compares server sessions, opaque tokens and JWT; recommends opaque access/rotating refresh to retain the explicit refresh/replay requirement without unneeded JWT keys.
- [Threat model](../security/identity-threat-model.md), [proposed OpenAPI](../api/identity-session.proposed.json) and [acceptance scenarios](../security/identity-acceptance.md) specify expiry/replay/logout/CSRF, safe failures, transaction/race behavior, sensitive logging and future tenant invariants. Implemented `openapi.yaml` stays unchanged.
- Local standard-library HTTP probe and seven tool tests support real observations after implementation. They are not a simulated auth implementation or evidence that security controls work.

## Current verification and limits

Proposed OpenAPI validates against the authoritative OAS3.0 schema and all local refs resolve. Eight Python tooling tests pass (seven probe mechanics + publisher regression), including a configured-proxy regression. Unchanged baseline API health passed on a temporary task-owned loopback18080 server, then the real proposed anonymous probe returned **FAIL: expected401, received404** because /me is absent. Fixture-dependent lifecycle probe returned **BLOCKED** without synthetic credentials. These are honest negative/prerequisite evidence, not passing product-security tests. Baseline server was stopped; caller's DB retained.

Java21 `mvn -B -f apps/api/pom.xml clean verify` PASS: 2 unit +7 real-PostgreSQL IT, no failures/errors/skips. Draft [PR #19](https://github.com/khaiminh0401/flowdesk/pull/19) targets main; actual [CI40343116480](https://github.com/khaiminh0401/flowdesk/actions/runs/40343116480) on review-fix commit `cd0c454` passed api/web/e2e. Logs confirm9 backend tests,8 tooling tests,18 Angular unit tests and4 live connectivity E2E tests; none are claimed as authentication acceptance. New code is limited to probe tooling; no application runtime, dependency, Flyway migration, authentication/session/cookie/authorization configuration or CI gate is changed. No deploy/public exposure or permission widening.

Known limits: backend CVE status remains unverified (previous Dependabot403/disabled); entity-free Hibernate validation checks no mappings; Playwright CI failure artifacts remain deferred TD-10. Local `.env` is ignored, uses caller's existing loopback55432 DB, and must not be printed/committed/reset casually.

## Next action and approval boundary

Human review of ADR-0002/model B, cookie/CSRF/lifetime/password/throttle defaults, strict duplicate-refresh reauthentication and first-slice provisioning scope is required. `AGENTS.md`: “Stop for human review before security-sensitive policy changes”. FD-010/#11 explicitly depends on that review. This session does not treat “continue” after merging the foundation PR as approval of a security policy that did not yet exist.

After explicit approval, record its reference/date and accepted changes, then plan small end-to-end FD-010 increments combining the relevant backend/migration contract with Angular behavior and real PostgreSQL/browser evidence, rather than isolated backend/frontend deliveries. Do not close FD-010 until its complete lifecycle acceptance is verified. Do not assume an unmerged design PR is on main. Workspace FD-011/#12 follows merged identity, with tenant authorization/write concurrency tests. Never merge or force-push automatically.

## Independent review and fixes

Review of69ad007..2bd1293 found no Critical defect and one Important probe safety defect: urllib automatically honored environment/system proxies. A new real-HTTP regression failed with a configured proxy and disabled bypass, then passed after explicit ProxyHandler({}); full tooling suite8/8 green. Two contract clarifications were also resolved: CSRF/origin is not protection against a stolen refresh credential used by a nonbrowser client; logout now defines valid-refresh plus expired/malformed/unknown-bearer fallback and the two-usable-family mismatch exception consistently across ADR/OpenAPI/acceptance. Review is not human policy approval.

Delivery commits: `5f15507` (probes), `2bd1293` (proposal), `0fe31c6` (proxy safety), `cd0c454` (review clarifications); final documentation update records the successful CI evidence. PR #19 remains draft, ADR Proposed, issue#10 open, human approval absent. Main stays69ad007; no merge or runtime auth change was made.
