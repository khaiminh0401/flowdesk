# Sprint 0 — Engineering Foundation

Milestone M0, due 2026-11-01. These criteria match the repaired GitHub issue bodies. All checkboxes remain open until evidence is reviewed; see [audit](sprint-0-audit.md).

## FD-001: Initialize monorepo & repository conventions

**Priority:** P0
**Estimate:** 2h
**Milestone:** M0

## Scope
Create new public FlowDesk repository with folder structure, README, .editorconfig, .gitignore, contributing guidelines and license.

## Acceptance criteria
- [ ] Repository is independent and follows documented conventions; no secrets committed.
- [ ] README distinguishes implemented Sprint 0 from planned M1/M2; contributor and security guides exist.

## Evidence
See the Sprint 0 hardening pull request and `docs/project/sprint-0-audit.md`. Keep this issue open until each criterion is verified.

## Notes
Do not change unrelated repositories.

## FD-002: Bootstrap Spring Boot application

**Priority:** P0
**Estimate:** 3h
**Milestone:** M0

## Scope
Create Java 21 Maven Spring Boot application with package-by-feature structure, health/info endpoints and baseline tests.

## Acceptance criteria
- [ ] Java 21: mvn -B -f apps/api/pom.xml clean verify runs meaningful unit and mandatory PostgreSQL integration tests.
- [ ] Boot context loads, /api/v1/info matches contract and /actuator/health returns UP against real PostgreSQL.
- [ ] Unit tests run without an external DB; ddl-auto=validate remains enabled and its no-entity limitation is documented.

## Evidence
See the Sprint 0 hardening pull request and `docs/project/sprint-0-audit.md`. Keep this issue open until each criterion is verified.

## Notes
Do not change unrelated repositories.

## FD-003: Bootstrap Angular application & routing

**Priority:** P0
**Estimate:** 3h
**Milestone:** M0

## Scope
Create standalone Angular application, shell, lazy dashboard routing, strict TS, lint and build.

## Acceptance criteria
- [ ] npm ci, npm run lint, npm test -- --watch=false and npm run build succeed with a committed lockfile.
- [ ] Strict standalone Angular shell renders a lazy dashboard and redirects unknown routes.
- [ ] Named navigation, skip link, current-page state and responsive layout are verified.

## Evidence
See the Sprint 0 hardening pull request and `docs/project/sprint-0-audit.md`. Keep this issue open until each criterion is verified.

## Notes
Do not change unrelated repositories.

## FD-004: Set up PostgreSQL, Flyway & Docker Compose

**Priority:** P0
**Estimate:** 3h
**Milestone:** M0

## Scope
Create local PostgreSQL configuration, Flyway V1 migration and environment example.

## Acceptance criteria
- [ ] docker compose config --quiet and docker compose up -d --wait db succeed; DB is healthy on a loopback host port.
- [ ] Flyway V1 is verified on real PostgreSQL, including expected tables and constraints.
- [ ] Environment export, configurable host port, credentials and destructive local reset procedure are documented.

## Evidence
See the Sprint 0 hardening pull request and `docs/project/sprint-0-audit.md`. Keep this issue open until each criterion is verified.

## Notes
Do not change unrelated repositories.

## FD-005: Set up GitHub Actions CI

**Priority:** P0
**Estimate:** 3h
**Milestone:** M0

## Scope
Build workflow for Maven verify, Angular lint and build.

## Acceptance criteria
- [ ] CI triggers on PR/push to main with read-only permissions, caches and bounded timeouts.
- [ ] Java 21 job runs unit tests, Testcontainers PostgreSQL tests and package verification without skip/fallback.
- [ ] Node 22 job uses npm ci and runs lint, headless Chrome tests and production build.
- [ ] Both actual GitHub Actions jobs pass on the pull request; no completion based on configuration alone.

## Evidence
See the Sprint 0 hardening pull request and `docs/project/sprint-0-audit.md`. Keep this issue open until each criterion is verified.

## Notes
Do not change unrelated repositories.

## FD-006: Write architecture & API contract

**Priority:** P0
**Estimate:** 5h
**Milestone:** M0

## Scope
Write MVP requirements, system context, module diagram, ERD draft, OpenAPI starter and ADR for modular monolith.

## Acceptance criteria
- [ ] Requirements, system context, module diagram, ERD draft and ADR reflect the modular monolith.
- [ ] OpenAPI describes implemented info and health endpoints; future business endpoints remain planned.
- [ ] Sprint 0 audit contains ranked findings, verification results, limitations and acceptance evidence.

## Evidence
See the Sprint 0 hardening pull request and `docs/project/sprint-0-audit.md`. Keep this issue open until each criterion is verified.

## Notes
Do not change unrelated repositories.
