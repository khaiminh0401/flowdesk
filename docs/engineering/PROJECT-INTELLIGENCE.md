# Project intelligence

Discovery: 2026-10-26. Baseline `origin/main` = `9d723b7` (merged PR [#7](https://github.com/khaiminh0401/flowdesk/pull/7)); main [CI 40293194920](https://github.com/khaiminh0401/flowdesk/actions/runs/40293194920) succeeded. This is a dated snapshot; fetch GitHub before relying on it.

## 1. Overview

FlowDesk targets small-team workspace, project, task and approval workflows for a Middle Full-Stack portfolio. [Requirements](../product/requirements.md) are an MVP outline, not a Sprint 1 specification. No Sprint 1 spec, identity implementation or M1 issue existed at discovery; new planning issues below do not prove completion.

## 2. Architecture map

One Boot deployable, one standalone Angular SPA, PostgreSQL/Flyway. [ADR-0001](../adr/0001-modular-monolith.md) is accepted. [Architecture map](ARCHITECTURE-MAP.md) distinguishes current nodes from future business modules. No microservices, queues or distributed transaction boundary exists.

## 3. Implemented modules

| Area | Evidence | Classification |
|---|---|---|
| API bootstrap/info | `apps/api/src/main/java/io/flowdesk/FlowDeskApplication.java`, `shared/api/InfoController.java` | Implemented/verified on main by InfoControllerTest + FoundationIT |
| DB foundation | `V1__create_identity_schema.sql`: app_users UUID/email/display_name/created_at | Implemented/verified by FoundationIT; not an identity domain/API |
| Angular shell/dashboard | `src/app/app.component.ts`, `app.routes.ts`, `features/dashboard` | Implemented/verified on main: 4 Chrome tests; static dashboard at discovery |
| Local/CI | Compose healthcheck/loopback; `ci.yml` api/web checks | Implemented/verified in PR #7 and main run above |
| Typed live dashboard connection | New SystemStatus service/component, proxy and Playwright | Current branch increment; acceptance evidence belongs in CURRENT-STATE, not inherited from main |
| Auth/session/workspace/projects/tasks/approvals/audit | Product outline, architecture draft diagrams | Planned; no services/entities/security filters/endpoints at baseline |

## 4. Technology inventory

| Layer | Declared version/source | Notes |
|---|---|---|
| JDK/Maven | Java21; Enforcer [21,22), Maven3.9+ in api/pom.xml | Exact runtime verified per session |
| Boot | 3.5.7 parent in api/pom.xml | Spring Web, validation, Actuator, JPA; no Spring Security |
| Persistence | Boot-managed PostgreSQL driver/Flyway/Hibernate | postgres:17-alpine in Compose/IT; patch-tracking image tag |
| Integration | Testcontainers1.21.4, Boot-testcontainers, Failsafe | Real DB; mandatory verify, no H2/skip |
| Web | Angular20.3 ranges, TS~5.9.3, RxJS~7.8.2 | Exact packages in package-lock; zoneless bootstrap |
| Browser tests | Karma/Jasmine + Chrome; Playwright added by connectivity increment | Unit HTTP boundary separate from live cross-stack smoke |
| Infrastructure | Compose v2, GitHub Actions | Node22/JDK21 caches; explicit read-only workflow permissions |

## 5. Key dependencies

JPA initializes without mapped entities; [FoundationIT](../../apps/api/src/test/java/io/flowdesk/FoundationIT.java) directly asserts SQL schema. Angular HTTP needs same-origin routing to API/aggregate health; development proxy is not a deployment router. Full verification needs Docker, PostgreSQL image/registry, Maven/npm registry and Chrome. Testcontainers1.21.4 addresses Docker29 compatibility, as recorded in [Sprint0 audit](../project/sprint-0-audit.md).

## 6. Constraints

Feature packages, one DB/deployable, immutable migrations, explicit server authorization when introduced. No auth/RBAC policy changes without review. No speculative state store or messaging. [AGENTS](../../AGENTS.md), [standards](ENGINEERING-STANDARDS.md) and [decision log](DECISION-LOG.md) govern future work.

## 7. Milestone and GitHub state

M0 main implementation is verified, but [#1–#6](https://github.com/khaiminh0401/flowdesk/milestone/1) remain OPEN with unchecked criteria. That is an operational acceptance gap, not evidence of missing code or permission to close blindly. M1–M6 are planning targets; no business milestone is implemented. [Roadmap](PRODUCT-ROADMAP.md) reflects the revised sequence (projects/tasks move to M2).

## 8. Technical debt

[TECHNICAL-DEBT](TECHNICAL-DEBT.md) tracks: missing identity policy/spec, no entity mapping validation yet, no automated migration upgrade scenario yet, unpinned DB image digest, legacy issue-draft scripts tied to initial M0, and no measured performance/deployment evidence. Stale Sprint0 draft/PR statements are historical, not current state.

## 9. Security concerns

No Security starter/filter/password hash/session store exists in pom/source. No auth or workspace isolation claim is valid. Current public endpoints reveal only app/stage and aggregate health. Backend defaults do not bind loopback; README's explicit local run argument does. [SECURITY-MODEL](SECURITY-MODEL.md) records threats and review requirements. GitHub Dependabot alerts could not be read: API403 says disabled and CLI lacks admin:repo_hook scope. No repository setting/scopes were changed; backend CVE coverage remains unverified.

## 10. Coverage gaps

No baseline committed E2E; previous browser smoke was a local artifact. Connectivity adds narrow committed live tests, not full product E2E. No auth/authorization/concurrency tests because those domains do not exist. No code-coverage percentage, load result, backup/restore or public deployment evidence exists. Keep [TEST-STRATEGY](TEST-STRATEGY.md) proportional to implemented behavior.

## 11. Next priorities

1. #9: preserve full-stack connectivity/error/retry evidence; no auth dependencies.
2. #8: commit and review this knowledge entry point/handoff with verified state.
3. #10: obtain review of identity/session threat model and ADR before #11 implementation.
4. Workspace isolation and M2+ follow merged prerequisites, not aspirational prompts. Consult GitHub links in the roadmap for actual issue numbers/status.
