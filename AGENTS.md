# FlowDesk agent entry point

## Mission and scope

Build an enterprise workspace/workflow portfolio demonstrating professional Java + Angular engineering. Deliver small, verified vertical slices; never label a plan as implemented. Work only in this repository. Read [CURRENT-STATE](docs/engineering/CURRENT-STATE.md), then inspect actual Git/GitHub state before resuming; snapshots are not automatically synchronized.

## Repository and stack

- `apps/api`: Java 21, Spring Boot 3.5.7, Maven 3.9+, feature packages under `io.flowdesk`, PostgreSQL 17/Flyway.
- `apps/web`: Angular 20, strict TypeScript, standalone/lazy features, signals/RxJS, npm lockfile, Node 22.12+ within 22.x.
- `docs/engineering`: intelligence, boundaries, standards, security/test strategy, roadmap and handoff.
- `docs/adr`, `docs/api`, `docs/product`: architectural decisions, OpenAPI, product requirements.
- `docker-compose.yml`, `.github/workflows/ci.yml`, `scripts`: local DB, checks and repo tooling.

## Engineering rules

Preserve the modular monolith and feature boundaries; use DTOs rather than exposing entities. Put future business transactions at application-service boundaries. Keep SQL migrations immutable once applied, use a new version, retain `ddl-auto=validate`. Do not add frameworks, global state stores, queues or deployment platforms without a concrete requirement and reviewed decision. See [architecture](docs/engineering/ARCHITECTURE-MAP.md) and [standards](docs/engineering/ENGINEERING-STANDARDS.md).

Use constructor injection for Java dependencies; Angular standalone components, typed HTTP boundaries and explicit loading/empty/error behavior. Keep examples synthetic. A static empty state is not proof that a business feature exists.

## Security and review boundaries

Backend authorization owns workspace isolation; route guards provide UX only. No authentication/session/RBAC exists until implemented and tested. Never commit secrets, print tokens, expose raw exceptions or weaken a failing security test. Keep local services on loopback. Review the [security model](docs/engineering/SECURITY-MODEL.md) before identity work.

Stop for human review before security-sensitive policy changes, destructive operations, unexpected infrastructure costs, public deployment, or changes outside the repo. Major architecture changes need an ADR before code. Never change tenant boundaries, session/cookie/token rules, applied migrations or CI gates merely to make tests green.

## Verification and definition of done

For software changes, write meaningful failing tests for changed behavior, then implement and verify. Use real PostgreSQL Testcontainers for integration; no H2 fallback or Docker-unavailable skips. Unit tests must not need an external DB. Run the [test strategy](docs/engineering/TEST-STRATEGY.md) commands: Java 21 clean verify; npm ci/lint/unit tests/production build; publisher regression; live Playwright for affected cross-stack flows. Record PASS/FAIL/BLOCKED accurately, including unavailable scanners. Do not fabricate screenshots, coverage, performance or CI status.

Done means acceptance criteria have evidence, actual PR checks pass, diff/secret patterns are reviewed, docs and current state match behavior, and known limits are explicit. Human merge/release acceptance is separate from implementation verification.

## Git, issues and PRs

Inspect working tree first and preserve user changes. Branch from the actual task base (`feat/<issue-id>-description`, `fix/...`, `docs/...`); never commit on main, rewrite history, force-push or merge automatically. Do not assume unmerged dependencies exist on main. Review existing issues before creating any; GitHub is the operational source of truth. Close issues only after every criterion is verified, never to inflate progress.

Use focused Conventional Commits. Push and open a draft PR with related issues, architecture/security impact, actual checks, limitations and review checklist; attach the PR to the chat when the tool is available. Do not send messages to others unless the user authorizes them.

## Resume and handoff

Read CURRENT-STATE and the active issue/PR, fetch remote refs, inspect diff/status/CI, and reconcile discrepancies before coding. Follow [roadmap](docs/engineering/PRODUCT-ROADMAP.md) dependencies and [decision log](docs/engineering/DECISION-LOG.md); an unresolved proposal is not an accepted policy. End substantial sessions by updating CURRENT-STATE with the actual base/branch, evidence, failures/blockers and next task. Preserve historical audit evidence as historical, with a clear date/commit.
