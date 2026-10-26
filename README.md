# FlowDesk

[![CI](https://github.com/khaiminh0401/flowdesk/actions/workflows/ci.yml/badge.svg)](https://github.com/khaiminh0401/flowdesk/actions/workflows/ci.yml)

> **Sprint 0 / In Development** — enterprise workspace & workflow management portfolio, built with Java 21, Spring Boot and Angular.

## Scope

The repository starts as a **modular monolith**: one Spring Boot deployable, feature-oriented Angular UI, PostgreSQL and reproducible local infrastructure. Features are implemented incrementally; authentication, workspace management, projects, Kanban and approval workflows are **planned, not yet implemented**.

## Prerequisites

- Java 21, Maven 3.9+, Node.js 22 LTS and npm 10+, Docker Compose
- Recommended: Angular CLI is not required globally (`npm run start`).

## Quick start

```bash
cp .env.example .env
# Use safe local credentials in .env and keep it out of Git.
docker compose up -d db
cd apps/api && mvn spring-boot:run
# In another terminal:
cd apps/web && npm install && npm run start
```

Backend: http://localhost:8080/actuator/health ; Frontend: http://localhost:4200

Spring Boot uses Flyway for DB migrations; the DB service must be healthy before API startup.

## Verification

```bash
cd apps/api && mvn -B verify
cd apps/web && npm install && npm run lint && npm run build
```

## Engineering approach

- Backend code is organized **by business feature**, not global controller/service/repository folders.
- DB schema changes via Flyway; avoid `ddl-auto=update`.
- Backend authorization owns business decisions; browser route guards alone are insufficient.
- Every non-trivial architecture change requires an ADR.
- CI is intended to run tests and builds; a badge is *not* evidence of passing until GitHub Actions has run.

## Documentation

- [Requirements](docs/product/requirements.md)
- [System context](docs/architecture/system-context.md)
- [Module architecture](docs/architecture/module-design.md)
- [Data model](docs/architecture/data-model.md)
- [API draft](docs/api/openapi.yaml)
- [ADR-0001](docs/adr/0001-modular-monolith.md)
- [Sprint 0 issue plan](docs/project/sprint-0-issues.md)
- [Publishing instructions](docs/project/publishing.md)

## Roadmap

| Milestone | Target |
|---|---|
| M0 — Foundation | Monorepo, API + web bootstraps, Postgres, migration, CI, specifications |
| M1 — Core | Auth, workspace RBAC, project CRUD |
| M2 — Workflow | Tasks, Kanban, approval & audit |
| M3 — Quality | E2E, integration/performance results |
| M4 — Operations | Deployment & observability |
| M5 — Release | v1.0 demo + interview walkthrough |

## Safety and status

This is a portfolio project, not a production service. It includes no real business data, production credentials or internal proprietary source. See [SECURITY.md](SECURITY.md). License: MIT.

> **Bootstrap limitation:** `package-lock.json` is not included because npm dependencies could not be resolved in the offline authoring environment. Run `npm install` once with registry access, commit the resulting lockfile, then switch CI to `npm ci`. The starter has not yet been compiled or executed against a running database.
