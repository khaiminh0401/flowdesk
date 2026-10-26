# Engineering brain and API connectivity implementation plan

Goal: give future sessions evidence-based repository guidance and prove a complete, read-only browser → API → PostgreSQL path before identity work.

Base: main `9d723b7`; PR #7 merged. No Sprint 1 specification or identity implementation exists in the repository or GitHub issues as of discovery. M0 #1–#6 remain open even though main CI run 40293194920 passed. This plan does not treat issue state as implementation evidence.

## Design and boundaries

Retain the modular monolith and public info/aggregate health endpoints. Replace the info Map with a response record without changing JSON. Add a small dashboard connection component, a typed HTTP service and same-origin development proxy. Requests have a five-second timeout; success requires nonempty info fields and health UP. Loading clears stale success; failure shows a safe generic message and explicit retry. Component destruction cancels requests. No tokens, cookies, credentials, CORS wildcard, auth policy, schema changes or global state store.

A standard Playwright test verifies live connectivity and controlled failure/recovery through the real dev proxy; existing tests isolate HTTP using Angular's testing backend. Playwright manages local API/web process lifecycles; Compose owns a disposable/local DB configured by the caller. CI creates test-only random credentials, starts PostgreSQL, and runs the same browser suite. Do not reuse preexisting servers in CI.

## Task 1 — Project brain and operational backlog

- [ ] Write AGENTS.md and nine engineering documents, citing source/tests/commits/issues.
- [ ] Reconcile M0–M6 without presenting planning targets as implemented.
- [ ] Create only missing milestones/labels and nonduplicate issues; keep current issue states unchanged.
- [ ] Record missing identity design and unavailable Dependabot alerts as explicit gaps.

## Task 2 — Typed API connectivity vertical slice

Files: `InfoController.java`, `InfoResponse.java`; `system-status.service.ts`, `system-status.component.ts`, corresponding specs; dashboard composition/spec, shell specs, bootstrap HTTP provider, dev proxy/angular config.

- [ ] Write service/component tests for loading, healthy success, HTTP/network/unhealthy/malformed failures, timeout, retry and cancellation. Run and observe missing implementation failure.
- [ ] Implement the minimal typed service, explicit state component and proxy, preserving existing dashboard copy and lazy routing.
- [ ] Run affected and complete Angular tests; verify backend JSON remains unchanged after replacing Map with record.

## Task 3 — Full-stack evidence and delivery

Files: Playwright config/spec, package/lockfile, CI E2E job, README, engineering verification/current state.

- [ ] Add Playwright scenarios for live API success, proxy failure + actual retry recovery, malformed payload and mobile layout. Run with real Boot/PostgreSQL/Angular.
- [ ] Run Java 21 clean verify, npm ci/lint/test/build, publisher regression and Compose validation. Preserve failure evidence and diagnose root causes.
- [ ] Review diff/credential patterns, independent read-only review, focused commits and draft PR; inspect actual CI on its head.
- [ ] Update CURRENT-STATE with actual results, outstanding policy review and next task. Never merge or force-push.

## Review focus

- Backend stopped/unreachable: bound waiting to five seconds and show retry, never raw errors.
- HTTP 200 with invalid info/health: reject it rather than render undefined/false success.
- Component destroyed while requests are in flight: cancel requests and avoid stale state updates.
- Existing route tests: flush real HTTP testing boundaries rather than mocking the status component.
- Same-origin production hosting: proxy is development-only; deployment must route API/health explicitly before publishing.
