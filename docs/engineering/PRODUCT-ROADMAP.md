# Product roadmap and dependency plan

Planning snapshot rechecked: 2026-10-30, baseline main `69ad007` after merged PR #18. GitHub issues/PRs are operational truth; this document is not synchronized automatically. Complexity is relative engineering scope, not a fabricated delivery date. Prefer complete vertical slices and split epics before implementation. Do not start a dependent slice against assumed unmerged code.

## M0 — Engineering Foundation

- **Objective:** a reproducible, tested modular-monolith starting point.
- **Features/deliverables:** monorepo conventions, Boot info/health, Angular shell, PostgreSQL/FlywayV1, automated checks, architecture docs; current increment adds Project Brain and live API connectivity.
- **Dependencies:** Java21/Maven3.9+, Node22/Chrome, Docker and registry access. Base foundation merged via PR #7.
- **Complexity:** medium; most baseline work implemented, operational acceptance remains distinct.
- **Acceptance:** fresh configured startup; strict lint/build/tests; real PostgreSQL migration/HTTP evidence; actual CI successful; documentation distinguishes future features; no committed secrets.
- **Testing:** isolated controller tests, mandatory Testcontainers, Angular Chrome tests, publisher regression; new connectivity live Playwright gate.
- **Risks:** unavailable Docker/registries, stale issue status, missing scanner coverage, dummy-test false confidence.
- **DoD/status:** baseline code verified on main run [40293194920](https://github.com/khaiminh0401/flowdesk/actions/runs/40293194920); #1–#6 still open for acceptance. #8/#9 code merged through PR #18; main CI40338793703 passed. Their issues remain open for operational acceptance.
- **Issues:** [FD-001–006](https://github.com/khaiminh0401/flowdesk/milestone/1), [FD-007 Project Brain #8](https://github.com/khaiminh0401/flowdesk/issues/8), [FD-008 connectivity #9](https://github.com/khaiminh0401/flowdesk/issues/9).

## M1 — Identity & Workspace

- **Objective:** authenticated users operate within correctly isolated workspaces.
- **Features/deliverables:** reviewed identity/session ADR and threat model; login/session recovery/logout, refresh rotation/reuse detection when that model is approved; workspace/member lifecycle and scoped permission matrix; Angular login/workspace UX; schema/API/security tests.
- **Dependencies:** merged M0; reviewed security policy before implementation; identity/session slice merged before workspace depends on it.
- **Complexity:** high; split identity and workspace into small reviewable slices.
- **Acceptance:** wrong/expired/revoked credentials handled safely, approved rotation/replay and cookie/CSRF behavior, server-enforced workspace RBAC, cross-tenant reads/writes denied, privilege/owner invariants hold under concurrency.
- **Testing:** real PostgreSQL security/transaction tests, accepted lifecycle cases, browser login/recovery/logout/workspace selection and allowed/denied membership actions.
- **Risks:** guessing token storage/expiry policy, bypassing backend checks, race conditions, sensitive logs. FD-009 supplies ADR-0002 and a proposed API/threat/test contract; human approval is still pending and no runtime security is implemented.
- **DoD/status:** policy proposal awaiting review; implementation planned. Design must be reviewed, slice acceptance and security invariants verified, actual CI green, docs/current state updated, human review/merge completed before dependents.
- **Issues/order:** [FD-009 design #10](https://github.com/khaiminh0401/flowdesk/issues/10) → [FD-010 session slice #11](https://github.com/khaiminh0401/flowdesk/issues/11) → [FD-011 workspace isolation #12](https://github.com/khaiminh0401/flowdesk/issues/12).

## M2 — Project & Task Management

- **Objective:** teams manage scoped project/task work from creation to Kanban transitions.
- **Features/deliverables:** project CRUD; task lifecycle, assignment, bounded filtering/pagination, Kanban; explicit validation/contracts/migrations and Angular feature views. Project CRUD moves here from the older README's M1 outline.
- **Dependencies:** merged/verified M1 identity and workspace boundaries; agree lifecycle/assignment/concurrency rules before code.
- **Complexity:** high epic; first deliver project creation/list with workspace scope, then task and board slices.
- **Acceptance:** all queries/mutations tenant-scoped; stable pagination/filters, valid assignment/transitions, concurrency behavior specified, accessible empty/loading/error UX.
- **Testing:** domain tests, PostgreSQL constraints/query/authorization tests, browser create/list/edit/task movement and denied cross-workspace scenarios.
- **Risks:** unbounded lists, N+1 queries, stale Kanban writes, UI-only permission checks.
- **DoD/status:** planned; split issues, accepted contracts, meaningful tests/CI/evidence, docs and human review for each complete vertical slice.
- **Tracking:** [FD-012 epic #13](https://github.com/khaiminh0401/flowdesk/issues/13).

## M3 — Approval & Audit

- **Objective:** make approval decisions consistent and traceable.
- **Features/deliverables:** reviewed approval state machine, server authorization, conflict handling, immutable history, Angular request/decision/history UX.
- **Dependencies:** merged M2 task lifecycle and M1 authorization; agree transitions/actors and audit retention semantics.
- **Complexity:** high; transactional/concurrency depth matters more than number of endpoints.
- **Acceptance:** exactly one accepted conflicting decision; denied transitions mutate nothing; audit append and state change commit atomically; tenant isolation applies to history.
- **Testing:** real concurrent PostgreSQL integration tests, rollback atomicity, actor/permission/state matrix, browser request/approve/reject/history flows.
- **Risks:** double approval, missing/incorrect audit events, mutable history, sensitive history exposure.
- **DoD/status:** planned; state/authorization invariants proved by automated tests, actual CI green, documented decisions/limits, reviewed merge before dependents.
- **Tracking:** [FD-013 epic #14](https://github.com/khaiminh0401/flowdesk/issues/14).

## M4 — Quality & Performance

- **Objective:** turn representative product quality claims into reproducible measurements.
- **Features/deliverables:** broader full-stack E2E/security/accessibility suites, measured DB query/index changes and benchmark environment/workload/results.
- **Dependencies:** representative M1–M3 flows and synthetic dataset; agree performance thresholds before running acceptance benchmarks. Narrow connectivity E2E already belongs to M0, not delayed until M4.
- **Complexity:** medium/high; depends on actual measured issues.
- **Acceptance:** critical workflows/security invariants automated, accessibility defects triaged, real query plans/measurements retained, no invented throughput/coverage numbers.
- **Testing:** repeatable workload scripts and E2E/security suites, before/after evidence under the same conditions.
- **Risks:** optimizing imagined bottlenecks, unstable fixtures, misleading environment comparisons, secret leakage in traces.
- **DoD/status:** planned; evidence can be reproduced, limitations stated, CI and relevant agreed thresholds met, changes reviewed.
- **Tracking:** [FD-014 epic #15](https://github.com/khaiminh0401/flowdesk/issues/15).

## M5 — Deployment & Observability

- **Objective:** deploy and operate the verified application safely and understandably.
- **Features/deliverables:** container artifacts, same-origin routing/TLS, runtime secrets, CI/CD, health/metrics and tracing where warranted, backup/restore and rollback runbooks.
- **Dependencies:** M4 release gates; human approval of hosting, security/public exposure and costs before deployment. Health endpoints currently exist; deployment evidence does not.
- **Complexity:** medium/high; choose the simplest hosting meeting real requirements.
- **Acceptance:** fresh target deployment/rollback reproducible; health/failure/backup restore exercised; secrets injected externally; routing and cookie policies verified in the approved environment.
- **Testing:** container smoke, readiness/failure, rollback and restore exercises with real retained evidence.
- **Risks:** accidental exposure, unexpected cost, insecure forwarded headers/cookies, untested backups.
- **DoD/status:** planned; approved target, tested operations, redacted evidence, reviewed docs and explicit release approval. No automatic deployment.
- **Tracking:** [FD-015 epic #16](https://github.com/khaiminh0401/flowdesk/issues/16).

## M6 — Portfolio Release

- **Objective:** communicate implemented engineering depth honestly in demos/interviews.
- **Features/deliverables:** professional README, diagrams, DB/transaction explanations, real screenshots/CI/benchmark links, synthetic demo scenarios and technical walkthrough.
- **Dependencies:** validated M5 target and M0–M4 acceptance evidence; human approval before external publication.
- **Complexity:** medium; documentation and rehearsal, not invention of missing features.
- **Acceptance:** walkthrough matches actual flows/version, demonstrates failure/security handling, every screenshot/metric references real execution, known limits remain explicit.
- **Testing:** rehearse documented demo on release candidate and verify links/artifacts/fixtures.
- **Risks:** presenting planned behavior as shipped, stale demo, sensitive data/screenshots.
- **DoD/status:** planned; versioned, reviewable release scope and verified evidence with human publication approval.
- **Tracking:** [FD-016 epic #17](https://github.com/khaiminh0401/flowdesk/issues/17).
