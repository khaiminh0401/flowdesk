# Sprint 0 — GitHub issue drafts

**Milestone:** M0 — Engineering Foundation (2026-10-26 through 2026-11-01)

## FD-001: Initialize monorepo & repository conventions

**Priority:** P0 · **Estimate:** 2h

### Scope
Create new public FlowDesk repository with folder structure, README, .editorconfig, .gitignore, contributing guidelines and license.

### Acceptance criteria
Repository is new and independent; README accurately labels project as Sprint 0; no credentials committed.

## FD-002: Bootstrap Spring Boot application

**Priority:** P0 · **Estimate:** 3h

### Scope
Create Java 21 Maven Spring Boot application with package-by-feature structure, health/info endpoints and baseline tests.

### Acceptance criteria
`mvn verify` passes in configured environment; `GET /actuator/health` is available when DB is running.

## FD-003: Bootstrap Angular application & routing

**Priority:** P0 · **Estimate:** 3h

### Scope
Create standalone Angular application, shell, lazy dashboard routing, strict TS, lint and build.

### Acceptance criteria
`npm ci`, lint and build succeed; dashboard route renders responsive shell.

## FD-004: Set up PostgreSQL, Flyway & Docker Compose

**Priority:** P0 · **Estimate:** 3h

### Scope
Create local PostgreSQL configuration, Flyway V1 migration and environment example.

### Acceptance criteria
`docker compose up -d db` healthy; API applies Flyway V1; no secrets committed.

## FD-005: Set up GitHub Actions CI

**Priority:** P0 · **Estimate:** 3h

### Scope
Build workflow for Maven verify, Angular lint and build.

### Acceptance criteria
CI triggers on PR/push to main and required checks are green before branch protection is enabled.

## FD-006: Write architecture & API contract

**Priority:** P0 · **Estimate:** 5h

### Scope
Write MVP requirements, system context, module diagram, ERD draft, OpenAPI starter and ADR for modular monolith.

### Acceptance criteria
Documentation distinguishes current implementation from future scope; diagrams and API contract are committed.

