# FlowDesk

[![CI](https://github.com/khaiminh0401/flowdesk/actions/workflows/ci.yml/badge.svg)](https://github.com/khaiminh0401/flowdesk/actions/workflows/ci.yml)

**Sprint 0 / In Development** — an enterprise workspace and workflow management portfolio demonstrating Java and Angular engineering.

## Implemented and planned

Implemented: Spring Boot foundation with `/api/v1/info` and Actuator health; standalone Angular shell with a lazy dashboard; PostgreSQL/Flyway V1; automated unit/integration tests and CI quality gates. One API deployable, feature-based packages, one SPA and one database form a modular monolith.

Planned: authentication, workspace RBAC, workspace management, project CRUD, Kanban, approval workflow and audit history. The dashboard retains its development/empty state and adds a read-only API connection card with loading, health validation and retry. The `app_users` table is schema groundwork, with no user API or JPA entity. This is a portfolio foundation, not a production deployment.

## Prerequisites

- JDK **21** and Maven **3.9+**. Maven rejects other Java majors. Check `java -version` and `mvn -version`; on macOS, use `export JAVA_HOME=$(/usr/libexec/java_home -v 21)` if needed.
- Node.js **22.12+ within 22.x**, npm **10+**. Angular 20.3 supports TypeScript 5.8–5.9; the lockfile selects TypeScript 5.9. No global Angular CLI needed.
- Docker Engine/Desktop running, Docker Compose v2 with `--wait`, registry access for PostgreSQL/Testcontainers images.
- Chrome/Chromium for Karma tests. Set `CHROME_BIN` to the browser executable if it is not discovered automatically. GitHub's Ubuntu runner includes Chrome.
- Python 3 for the issue-publisher regression test; GitHub CLI only for repository administration.

## Clone → configure → database → backend → frontend

Commands below use Bash or Zsh and start at the repository root.

```bash
git clone https://github.com/khaiminh0401/flowdesk.git
cd flowdesk
cp .env.example .env
# Edit .env: replace both password placeholders with the SAME local password.
# Keep POSTGRES_DB/USER and SPRING_DATASOURCE_URL/USERNAME aligned.
# If 5432 is occupied, change POSTGRES_PORT and the port in SPRING_DATASOURCE_URL together.
docker compose config --quiet
docker compose up -d --wait db
docker compose ps

# Compose reads .env automatically; Maven/Spring Boot does not.
# Export the trusted local file in this terminal before starting the backend.
set -a
source .env
set +a
mvn -f apps/api/pom.xml spring-boot:run -Dspring-boot.run.arguments=--server.address=127.0.0.1
```

In another terminal, from the repository root:

```bash
cd apps/web
npm ci
npm start
```

API: [health](http://localhost:8080/actuator/health), [info](http://localhost:8080/api/v1/info). Web: [dashboard](http://localhost:4200). The web dev server and database bind to loopback. Spring Boot starts Flyway before Hibernate validation. Never change an applied migration: add V2 for the next schema change.

```bash
curl --fail http://localhost:8080/actuator/health
# {"status":"UP",...}
curl --fail http://localhost:8080/api/v1/info
# {"application":"FlowDesk","stage":"sprint-0"} (key order may vary)
```

The Angular dev server proxies `/api/**` and `/actuator/health` to the loopback API on port8080. The connection card requires both valid info and health UP; it shows a bounded, retryable error if the API/DB is unavailable. The proxy is development-only: production hosting must route these same-origin URLs explicitly. Authentication and authorization do not exist yet; do not expose the API publicly.

## Verification

From the repository root, with Java 21 and Docker available:

```bash
mvn -B -f apps/api/pom.xml clean verify
python3 -m unittest discover -s scripts/tests
cd apps/web
npm ci
npm run lint
npm test -- --watch=false
npm run build
```

`mvn test` runs database-free controller contract tests. `mvn verify` additionally runs `*IT` with Failsafe against a disposable **real PostgreSQL 17 Testcontainer**, a random port, Boot context, HTTP, Flyway and schema constraints. No H2, external local database or `.env` is needed for either test command. Missing Docker fails integration verification; tests are never silently skipped. Both Maven test phases fail if no tests are discovered.

Frontend unit tests run the real shell, lazy routes, fallback route, dashboard and connection states in headless Chrome. TypeScript and template checking stay strict. `npm run build` explicitly selects production with bundle budgets. CI runs the same Maven verify and npm commands with caches, read-only permissions and job timeouts. A badge alone is not proof: check the PR's actual run. See the [audit and acceptance evidence](docs/project/sprint-0-audit.md).

## Live end-to-end tests

With Chrome installed, configure/export `.env` and start the DB as above, then run `npm run e2e --prefix apps/web` from the root. Playwright starts its own API8080 and Angular4200 processes and stops them afterward; those ports must be free. It uses the installed Chrome, so a separate browser download is not required. Tests prove live proxy/API/DB connectivity, safe failure/retry recovery, malformed-response handling and mobile layout. They do not imply login or business workflows exist. See [test strategy](docs/engineering/TEST-STRATEGY.md).

## Stop and reset the local database

`docker compose stop db` retains data; `docker compose down` removes this project's containers/network while retaining the named volume. To **erase this checkout's local database**, stop the backend first, then run:

```bash
docker compose down --volumes
docker compose up -d --wait db
# Restart the backend using the exported .env; Flyway recreates V1 on the empty DB.
```

Only reset disposable local data. PostgreSQL initialization variables do not change existing volume credentials: changing passwords in `.env` alone does not reset a populated database.

## Engineering decisions

- Keep one modular monolith; use business feature packages as features arrive. No speculative microservices, queues or global state store.
- Keep V1 unchanged; test its SQL directly. Hibernate `ddl-auto=validate` starts successfully, but **no entity mappings exist yet**, so it cannot validate `app_users` against a JPA model. Revisit mapping validation when M1 introduces entities.
- Use Angular 20 zoneless change detection explicitly, standalone components and lazy routes. Karma/Jasmine uses the supported Angular 20 builder; the experimental Vitest 3 path was rejected during this audit after dependency advisories.
- The live connection card uses `aria-busy`, polite loading/success, an actionable safe error/retry state and five-second request timeout; malformed responses never appear connected. Business empty states remain distinct.
- No production credentials are supplied. `.env.example` contains local placeholders; `.env` and generated build artifacts are ignored. Deployments must inject credentials separately.

## Documentation and roadmap

[Agent entry point](AGENTS.md) · [Current engineering state](docs/engineering/CURRENT-STATE.md) · [Detailed roadmap](docs/engineering/PRODUCT-ROADMAP.md) · [Requirements](docs/product/requirements.md) · [System context](docs/architecture/system-context.md) · [Module design](docs/architecture/module-design.md) · [Data model](docs/architecture/data-model.md) · [OpenAPI](docs/api/openapi.yaml) · [ADR-0001](docs/adr/0001-modular-monolith.md) · [Sprint 0 issues](docs/project/sprint-0-issues.md) · [Contributing](CONTRIBUTING.md)

| Milestone | Scope |
|---|---|
| M0 | Engineering foundation, verified before moving on |
| M1 | Identity, sessions, workspace RBAC and workspace management |
| M2 | Projects, tasks, assignment, filtering and Kanban |
| M3 | Approvals, concurrency and immutable audit |
| M4 | Broader E2E, accessibility, security and measured performance |
| M5 | Deployment and observability |
| M6 | Portfolio release and interview walkthrough |

No real business data or proprietary source is included. [Security policy](SECURITY.md). MIT license.
