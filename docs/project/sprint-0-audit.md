# Sprint 0 audit — 2026-10-26

Baseline: `92a2e01` on remote main. Supplied folder had no Git metadata and lacked the remote lockfile; Git metadata was reconstructed without replacing working files, on `fix/FD-005-sprint0-audit-hardening`. No other supplied source differed from main. Six open issues belong to M0 — Engineering Foundation, due 2026-11-01.

## Findings before implementation

No P0 finding identified. Priorities below describe risks in the baseline, not claims of active exploitation.

| Priority | Location | Finding and consequence |
|---|---|---|
| P1 | `apps/api/src/test/java/io/flowdesk/FlowDeskApplicationTests.java` | Class-existence assertion cannot detect application startup, HTTP, migration or DB failures. No real PostgreSQL tests. |
| P1 | `apps/api/pom.xml` | No Testcontainers or Failsafe lifecycle. A green verify provides no integration evidence. |
| P1 | `README.md`, `.env.example`, `application.yml` | Compose reads `.env`, Maven does not. Documented startup leaves backend password empty; credentials must be exported. |
| P1 | `apps/web/angular.json`, `package.json` | Test target has no runner dependencies, spec config or tests. Production bootstrap uses Zone-based Angular without importing Zone. |
| P1 | `.github/workflows/ci.yml` | Uses npm install, omits frontend tests and integration gate, lacks explicit permissions/timeouts. |
| P1 | `scripts/create-sprint0-issues.sh`, GitHub #1–#6 | Shell backslash replacement corrupts literal n characters and Markdown in published issue bodies. |
| P2 | `README.md` | Claims lockfile absent despite remote main tracking it; verification omits frontend tests and DB reset steps. |
| P2 | `docs/architecture/system-context.md` | Authorization statement could imply enforcement exists; auth remains planned. |
| P2 | `apps/web/src/app/app.component.ts`, `src/styles.scss` | Navigation lacks accessible naming/current-page/skip link; mobile grid stretches navigation to about 320px. |
| P2 | `docs/api/openapi.yaml` | Health endpoint and exact info response values unspecified. |

## Implementation and validation plan

Preserve Java 21 / Boot 3.5.7, Angular 20 strict standalone/lazy routing, PostgreSQL 17, feature packages and immutable V1. No M1 features or production entities are added merely to make ORM validation appear meaningful.

- [x] Backend: replace superficial test with database-free HTTP contract tests; add mandatory Testcontainers PostgreSQL context/HTTP/migration/schema/constraint tests under Failsafe; keep ddl-auto=validate and state its current limits.
- [x] Web: repair runner and strict spec config, test actual shell navigation/lazy route/fallback and dashboard status; add accessibility semantics; install with committed lockfile; verify production bootstrap.
- [x] Infrastructure/CI: environment export instructions, loopback services, health wait, unit/integration split, npm cache/ci/tests, least permissions/timeouts.
- [x] Documentation/issues: accurate implementation boundary, API contract, technical decisions, checked acceptance matrix, repair issue publishing and issue bodies without closing unverified work.
- [x] Verification: Java 21 clean verify, npm ci/lint/test/build, Compose config/start/health, HTTP smoke, diff/secrets review, focused commits, push and draft PR; inspect actual CI.

Local execution and actual PR CI evidence are recorded below. Resolved initial failures are retained for traceability.

## Changes and decisions

- Backend: Enforcer requires JDK 21/Maven 3.9; Surefire isolates controller tests from DB startup, Failsafe runs mandatory `FoundationIT` with a Boot random-port server and PostgreSQL 17. Both fail on zero discovered tests. Testcontainers 1.21.4 supports this host's Docker 29 (the older Boot-managed line has Docker API compatibility issues).
- Frontend: strict standalone/lazy routing retained; explicit zoneless bootstrap fixes missing Zone runtime. Karma/Jasmine replaces the incomplete experimental unit-test target. A trial of Angular 20's supported Vitest 3 introduced critical npm advisories and was removed; the final lockfile audits clean at verification time. Shell tests drove named navigation, skip link and current-page semantics. Production build has an initial bundle budget.
- CI: Java 21 and Node 22 jobs run clean verify / npm ci, lint, Chrome tests and production build. Read-only permissions, per-job timeouts and cancellation for superseded commits. No redundant service DB: Testcontainers owns integration lifecycle.
- Local: `.env` export is explicit; Compose uses a configurable loopback port. Host 5432 was occupied, so this verification used 55432 without stopping any other service. The first startup attempt failed on the occupied port; recreating only FlowDesk's newly created DB on 55432 resolved it.
- Issues: all six remote bodies were corrupted by shell backslash replacement. A failing fake-CLI regression reproduced the defect; stdin-based publishing passes. All six bodies were repaired and read back byte-for-byte, with M0 membership retained and acceptance criteria clarified. Issues remain open; no auto-close keywords are used.

## Local verification — 2026-10-26

| Command/check | Result | Evidence |
|---|---|---|
| `JAVA_HOME=<JDK21> mvn -B -f apps/api/pom.xml clean verify` | PASS | 2 unit + 7 integration tests, zero failures/errors/skips; repackaged executable JAR. |
| `DOCKER_HOST=tcp://127.0.0.1:1 mvn -B -f apps/api/pom.xml test` under JDK21 | PASS | 2 controller tests with no database/container startup. |
| `npm ci` in apps/web | PASS | Fresh install from committed lockfile. |
| `npm run lint` | PASS | TypeScript + inline/external template rules, zero warnings. |
| `npm test -- --watch=false` | PASS | 4 real Angular tests in headless Chrome: shell landmarks, lazy route/current link, unknown-route redirect, dashboard development/empty state. |
| `npm run build` | PASS | Production bundles generated within budget, lazy dashboard chunk retained. |
| `npm audit` | PASS | 0 reported vulnerabilities in the final dependency graph at verification time. Not a comprehensive security assessment. |
| `python3 -m unittest discover -s scripts/tests` | PASS | Issue bodies survive publishing exactly; fake CLI performs no network mutation. |
| `docker compose config --quiet` | PASS | Local ignored `.env`; no resolved credentials printed or committed. |
| `docker compose up -d --wait db`, `docker compose ps` | PASS | FlowDesk PostgreSQL 17 healthy on 127.0.0.1:55432 after resolving local port conflict. |
| API HTTP and SQL smoke | PASS | Running API: health UP, expected info JSON. Local Flyway history contains successful V1. |
| Production frontend browser smoke | PASS | Built SPA served on loopback; headless Chrome rendered lazy dashboard and current navigation, outside TestBed. CDP checks at 390/1280px show no horizontal overflow; mobile navigation stays at its natural height. Screenshots inspected locally, not fabricated or committed. |
| GitHub issue readback | PASS | #1–#6 exact repaired bodies and M0 membership. |
| GitHub Actions on PR | PASS | [Run 40284986400](https://github.com/khaiminh0401/flowdesk/actions/runs/40284986400) on implementation commit `b798637`: api and web both successful; CI logs confirm 2 unit + 7 IT and 4 Chrome tests actually ran. |

## Acceptance matrix

Statuses concern evidence on this branch, not a claim that unmerged main already contains these changes.

| Issue | Status | Acceptance evidence |
|---|---|---|
| FD-001 / #1 | PASS | Independent repo, feature branch, conventions/license/security guide, accurate scope; ignored local credentials and tracked-diff review. |
| FD-002 / #2 | PASS | Java 21 clean verify, context + live HTTP on real PostgreSQL, isolated unit suite; validation limitation below. |
| FD-003 / #3 | PASS | Locked install, strict lint, 4 Chrome tests, production build/browser smoke; desktop/mobile shell review. |
| FD-004 / #4 | PASS | Healthy Compose DB, local and disposable-DB V1 execution, schema/constraints, documented environment and reset. |
| FD-005 / #5 | PASS | Actual api/web PR jobs passed in run 40284986400; logs confirm tests executed. |
| FD-006 / #6 | PASS | Requirements/diagrams/ADR distinguish plans; current API/health contract, audit and trade-offs documented. |

## Limits and work before M1

- All six acceptance rows have branch-level evidence, including successful actual api/web PR jobs. The six issues stay open for maintainer acceptance and the PR stays draft. Main is unchanged; review/merge and issue closure remain before adopting this foundation for M1. Branch protection is a maintainer decision.
- No JPA entities exist. `ddl-auto=validate` is confirmed as active at startup, but direct SQL integration assertions—not ORM mappings—verify V1. Add entity/migration validation with actual M1 entities.
- Local `.env` uses generated credentials and port 55432 only for this checkout. A clone must configure its own credentials. Existing initialized DB volumes keep their old passwords.
- Chrome and Docker are required for full verification; dependency registries/image tags are external availability inputs. PostgreSQL 17 tags track patches intentionally; this is not byte-for-byte container reproducibility.
- npm reports upstream deprecation notices (including Angular animations and older Karma transitive utilities). Zero audit findings does not prove absence of vulnerabilities. No production deployment, authentication, RBAC or business feature was added.

## Reference checks

Angular compatibility was checked against https://angular.dev/reference/versions; the installed Angular 20 builder schemas determined runner options. Testcontainers Docker compatibility: https://github.com/testcontainers/testcontainers-java/releases/tag/1.21.4. Boot service connections: https://docs.spring.io/spring-boot/3.5/reference/testing/testcontainers.html.

## Review and delivery

Draft PR: https://github.com/khaiminh0401/flowdesk/pull/7 against main, branch `fix/FD-005-sprint0-audit-hardening`. Focused implementation commits: `df6e686` (backend), `8a63060` (web), `b336ff9` (CI/local tooling), `b798637` (documentation). A final documentation-only commit records CI evidence.

Read-only independent review of `92a2e01..b798637` found no Critical or Important defects. Its one Minor finding (stale future-tense audit text) was corrected with this evidence update. Review scope excluded rerunning supplied smoke results, changing branch protection, and implementing future auth/entity behavior; the primary run verified actual CI, issue readback, browser/HTTP/Compose and npm audit directly.

`npm start -- --port 4201` was also started successfully and its HTML fetched, validating the documented Angular development-server path in addition to the production browser smoke. No public deployment or merge occurred.
