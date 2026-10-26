# Technical debt and gaps

Priorities describe engineering risk, not a claim of exploitation. Discovery baseline main `9d723b7`; current-session evidence in CURRENT-STATE.

| ID / priority | Evidence and effect | Resolution / dependency |
|---|---|---|
| TD-01 / P1 | No detailed identity/session spec, Security starter or security filters (`pom.xml`, `io.flowdesk` source). Business features cannot safely depend on guessed policies. | #10 design/ADR reviewed before #11 implementation. |
| TD-02 / P1 | Dependabot API403: alerts disabled and CLI scope unavailable. Maven tests are not a vulnerability scan. | Maintainer-approved scanner/settings review; no clean-backend-CVE claim. Do not broaden permissions autonomously. |
| TD-03 / P2 | `ddl-auto=validate` active with zero entities; FoundationIT checks SQL directly. No ORM mapping validation yet. | Add/test actual mappings with first M1 domain entity; do not create dummy entities. |
| TD-04 / P2 | Only V1 exists; FoundationIT proves clean install/checksum/constraints, not an upgrade across schema versions. | Add previous-version → next-version migration scenario when V2 is introduced. |
| TD-05 / P2 | Compose/IT use postgres:17-alpine rather than digest; patches can change across runs. | Track patched image deliberately; evaluate immutable digests/updates before deployment. No byte-for-byte reproducibility claim. |
| TD-06 / P2 | No committed E2E on baseline; CI had only isolated app suites. | #9 adds minimal live connectivity/browser failure-retry gate. Broad auth/business E2E stays M1–M4 work. |
| TD-07 / P2 | `scripts/issue-data.json` describes original M0; issue status is maintained on GitHub. Historical audit says PR #7 draft at that time. | Label historical docs clearly; use CURRENT-STATE/live GitHub for current state rather than auto-sync claims. |
| TD-08 / P2 | No performance, deploy/restore, tracing or production-routing evidence in repo. | M4 measurement and M5 approved operations; no premature platform additions. |
| TD-09 / P2 | package.json retains unused animations/zone dependencies and upstream Karma deprecation notices. | Review removal when touching dependency baseline; do not mix broad churn into connectivity slice. Audit current dependency graph each session. |

Closed/resolved debt should retain a dated evidence link. Do not turn all missing future features into urgent bugs; roadmap dependencies distinguish intentional deferral from regression.
