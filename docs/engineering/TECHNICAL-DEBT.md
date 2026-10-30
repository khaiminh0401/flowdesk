# Technical debt and gaps

Priorities describe engineering risk, not a claim of exploitation. Discovery baseline main `9d723b7`; current-session evidence in CURRENT-STATE.

| ID / priority | Evidence and effect | Resolution / dependency |
|---|---|---|
| TD-01 / P1 | ADR-0002/proposed contract now describe identity/session policy, but human approval is pending. No Security starter/filter exists (`pom.xml`, `io.flowdesk` source). Business features must not depend on an unaccepted proposal. | #10 design/ADR reviewed before #11 implementation. |
| TD-02 / P1 | Dependabot API403: alerts disabled and CLI scope unavailable. Maven tests are not a vulnerability scan. | Maintainer-approved scanner/settings review; no clean-backend-CVE claim. Do not broaden permissions autonomously. |
| TD-03 / P2 | `ddl-auto=validate` active with zero entities; FoundationIT checks SQL directly. No ORM mapping validation yet. | Add/test actual mappings with first M1 domain entity; do not create dummy entities. |
| TD-04 / P2 | Only V1 exists; FoundationIT proves clean install/checksum/constraints, not an upgrade across schema versions. | Add previous-version → next-version migration scenario when V2 is introduced. |
| TD-05 / P2 | Compose/IT use postgres:17-alpine rather than digest; patches can change across runs. | Track patched image deliberately; evaluate immutable digests/updates before deployment. No byte-for-byte reproducibility claim. |
| TD-06 / P2 | No committed E2E on baseline; CI had only isolated app suites. | #9 adds minimal live connectivity/browser failure-retry gate. Broad auth/business E2E stays M1–M4 work. |
| TD-07 / P2 | `scripts/issue-data.json` describes original M0; issue status is maintained on GitHub. Historical audit says PR #7 draft at that time. | Label historical docs clearly; use CURRENT-STATE/live GitHub for current state rather than auto-sync claims. |
| TD-08 / P2 | No performance, deploy/restore, tracing or production-routing evidence in repo. | M4 measurement and M5 approved operations; no premature platform additions. |
| TD-10 / P2 | Playwright retains failure traces/screenshots only on the runner/local disk; CI does not upload them. No failure artifacts survive the ephemeral runner. | Optional failure-only upload of scoped synthetic test artifacts with short retention; deferred minor from review, no test correctness blocker. |
| TD-09 / P2 | package.json retains unused animations/zone dependencies and upstream Karma deprecation notices. | Review removal when touching dependency baseline; do not mix broad churn into connectivity slice. Audit current dependency graph each session. |
| TD-11 / P2 | [CI41015107926](https://github.com/khaiminh0401/flowdesk/actions/runs/41015107926) annotations flag Node20 action runtimes (runner forces Node24), setup-java v4 deprecation and ubuntu-latest migration. Current api/web/e2e gates passed. | Review supported checkout/setup-java/setup-node releases and runner baseline in a focused CI change; preserve required gates and verify actual runs. |

2026-10-30 review follow-up: PR #19 probe hostname routing and related cookie/response-validation defects are addressed with failing-first local HTTP regressions. Proposed-contract review concerns remain under TD-01/#10: login/account-switch cookie read scope and explicit OpenAPI logout/error/header/input constraints. These are not approved runtime behavior.

Closed/resolved debt should retain a dated evidence link. Do not turn all missing future features into urgent bugs; roadmap dependencies distinguish intentional deferral from regression.
