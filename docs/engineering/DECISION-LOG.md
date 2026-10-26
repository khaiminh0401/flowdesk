# Engineering decision log

| Date | Decision / status | Evidence / trade-off |
|---|---|---|
| 2026-10-23 | Accepted: modular monolith | ADR-0001; one deployable/DB preserves transactions and simple operations. No evidence for distributed services. |
| 2026-10-26 | Implemented on main: strict standalone Angular, explicit zoneless bootstrap, Karma/Jasmine | PR #7, `8a63060`; keep Angular20. Experimental Vitest3 trial removed after advisories. |
| 2026-10-26 | Implemented on main: mandatory real PostgreSQL integration gate | PR #7, `df6e686`, FoundationIT; no H2/skips. Entity-free validation limitation is explicit. |
| 2026-10-26 | Local operational choice: loopback API startup argument | `920cce6` merged in `9d723b7`; default application YAML still binds unless configured. |
| 2026-10-26 | Current increment: read-only connectivity before identity policy | #9; uses existing info/aggregate health, typed DTO/HTTP, same-origin proxy and live E2E. No authentication/security policy change. |
| 2026-10-26 | Current increment: establish repository knowledge entry point | #8; concise AGENTS links detailed docs; GitHub remains operational truth, handoff is a dated snapshot. |
| 2026-10-26 | Proposed/pending review: M1 identity/session design | #10; do not choose JWT/session, token storage, CSRF, cookie or expiry policy merely from a stack keyword. Obtain review of threat model/API/ADR first. |

Reconcile issue links against the live roadmap. Later implementation may supersede a decision, but preserve rationale/history rather than rewriting old evidence. No new major architecture ADR is warranted for consuming existing public diagnostics. A new identity/session policy does require one.
