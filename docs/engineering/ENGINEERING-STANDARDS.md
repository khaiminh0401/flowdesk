# Engineering standards

Read [AGENTS](../../AGENTS.md) first. These conventions preserve [ADR-0001](../adr/0001-modular-monolith.md); they do not claim future infrastructure is implemented.

## Backend

Use Java21, Boot-managed dependency versions and feature packages. Controllers accept/return explicit API DTOs; constructor-inject required collaborators. Validate input at public boundaries and business invariants inside the domain/application service. Add transaction boundaries for the atomic business operation, not a blanket annotation on controllers. Use parameterized queries/JPA and stable, bounded pagination when introduced.

Handle expected errors consistently with the API contract (problem responses are proposed for M1, not currently wired). Never return stack traces, SQL details or sensitive credentials. Do not add a generic exception framework for the current read-only info endpoint. No production entities or empty modules solely to satisfy architecture diagrams.

Flyway is the schema owner. Never alter applied V1; introduce forward migrations and test fresh + upgrade paths as schema evolution begins. Keep `ddl-auto=validate`, `open-in-view=false`. Use DTOs/projections for user-facing data rather than serializing entities or triggering lazy loads from HTTP rendering.

## Angular

Strict TypeScript/template checks stay enabled. Use standalone components and lazy feature routes; keep feature state local through signals and bounded RxJS streams. Typed interfaces do not validate remote JSON: validate untrusted payloads where behavior depends on fields. Use Reactive Forms with real validation when forms arrive; guards/interceptors only when a concrete feature needs them.

Loading must not display stale success. Empty data and request failure are distinct states. Provide a bounded wait, actionable retry and cancellation on destruction; avoid automatic unbounded retries. Use semantic landmarks/headings/labels, keyboard-operable controls, visible focus and mobile layouts. Interpolate untrusted strings; do not bypass sanitization.

## Review and documentation

Keep commits/PRs reviewable. Cite the actual issue and test result, including blocked checks. Do not assume unmerged dependencies are on main. No force-push, automatic merge or unrelated repo edits. Do not close issues just because a PR is merged.

For major architecture/security changes, write a reviewed ADR before implementation. For routine implementation choices, update [DECISION-LOG](DECISION-LOG.md) without inflating every choice into an ADR. Update OpenAPI when the public contract changes, roadmap when scope/dependencies change, debt when a concrete gap is found, and CURRENT-STATE after substantial work.

Definition of Done: explicit acceptance + meaningful tests, all relevant commands and actual PR CI green, secret/diff review, accurate docs, limitations and human review path. See [test strategy](TEST-STRATEGY.md).
