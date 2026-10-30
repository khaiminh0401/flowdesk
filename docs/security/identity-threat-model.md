# Identity/session threat model — proposed

Date2026-10-26, FD-009/#10, base main69ad007. No controls in this document are implemented by this PR. Decisions depend on [ADR-0002](../adr/0002-identity-session-lifecycle.md) acceptance; tests are specified in [identity acceptance](identity-acceptance.md).

## Assets and boundaries

Passwords/hashes, raw opaque access/refresh credentials, CSRF state, user/family identity, workspace membership and future tenant data. Browser JS is less trusted than backend; HttpOnly cookie protects read access but not an XSS-driven action. API trusts neither client IDs/roles nor arbitrary forwarding/origin headers. PostgreSQL owns durable family/replay state; servlet memory holds only CSRF state. Same-origin TLS terminator/hosting is a separate future deployment boundary requiring explicit configuration.

Attackers include unauthenticated remote callers, malicious websites/subdomains, stolen-token holders, malicious authenticated members and concurrent/stale clients. DB/host compromise is not solved by token hashing; key/secret/runtime access requires operational controls outside this local slice.

| Threat | Proposed control / invariant | Acceptance ID |
|---|---|---|
| Credential stuffing/account enumeration | Generic login response, equivalent hash verification path, account+IP temporary throttles for existing and unknown names; no permanent attacker-triggered lockout | I-01/I-02/I-03 |
| Offline password cracking | Argon2id parameters encoded with salt, update policy on legitimate login; no plaintext/sensitive logs | I-04/I-15 |
| Session fixation | Never accept an existing anonymous/auth cookie as new login identity; mint new token family, rotate CSRF session ID and invalidate old CSRF | I-05/I-06 |
| Refresh replay/races | Single-use DB state, family lock/atomic consume+replacement; consumed token revokes family durably before generic401 | I-07/I-08/I-09 |
| Revoked/expired access still authorizes | Central family/user/expiry checks, exact time boundary; no stateless JWT bypass | I-10/I-11 |
| CSRF/login-CSRF/logout-CSRF | Framework synchronizer token + exact Origin on unsafe methods; SameSite defense in depth; refresh cookie alone never authenticates protected APIs | I-06/I-12/I-13 |
| XSS/token exfiltration | Angular escaping, no bypassSecurityTrust/innerHTML for remote fields, tokens memory-only, HttpOnly refresh, no URL/log persistence. XSS remains able to act as user; future CSP/dependency review still required | I-14/I-15 |
| Cookie injection/session mixup | Secure host-only __Host- cookies in HTTPS profile; explicit loopback-only dev exception, no Domain; matching family for bearer+refresh credentials when both supplied | I-13/I-16 |
| IDOR/BOLA/cached role escalation | Workspace-scoped server queries, current membership/role, no client/token role authority, same-transaction checks and revocation ordering | W-01/W-02/W-03 |
| State-store loss/failure | Safe503, no token issued before commit, no partial rotation or rolled-back replay revocation; CSRF restart bootstraps rather than disabling validation | I-09/I-17 |
| Cross-origin/token leakage | No credentialed wildcard CORS; interceptor never sends bearer externally, no-store; don't leak errors/token identifiers | I-14/I-15 |
| Resource exhaustion | Bound input/hash concurrency, login/CSRF session creation and cleanup; consumed hashes retained through family expiry | I-03/I-18 |

## Residual risks and explicit trade-offs

- An attacker holding a raw still-unused refresh token can bootstrap their own CSRF session and spoof the configured Origin using a nonbrowser client, then win a rotation. A family is not bound to its original CSRF session; CSRF/Origin controls prevent browser cross-site attacks, not bearer-token theft. Subsequent detected reuse revokes the family. HttpOnly is not a cure for malware/XSS or host compromise.
- Two legitimate refreshes can revoke a family; no replay grace window is hidden. Frontend single-flight reduces incidence but cannot make distinct browser clients atomically share memory tokens. Reauthentication is the proposed user-visible outcome.
- Central DB lookup costs more than local JWT verification. No performance claim exists; measure representative queries before adding caching that could weaken revocation.
- Temporary account-based throttles can cause denial of login to a known account; IP limits can affect shared networks. Values are reviewable policy defaults; deployment/proxy trust and monitoring are mandatory before public exposure.
- CSRF state is single-process memory; restart recovery is specified, multiple replicas are not. Anonymous session creation must be bounded before production. This proposal does not authorize public rollout.
- No registration/email verification/reset/MFA/recovery workflow, production seed, tenant permission matrix or operational recovery procedure is silently considered implemented. Scope/rollout decisions remain human-reviewed.

## Logging and evidence boundary

Record event metadata and internal opaque IDs only. Redact passwords, password hashes, raw access/refresh/CSRF tokens, cookies, Authorization and bodies from logs, traces, screenshots and exceptions. Integration tests inspect captured logs with sentinel synthetic credentials; CI artifacts must be scoped and reviewed before upload. Actual security acceptance requires real Boot/Spring Security/PostgreSQL tests and browser flows, not this threat table or the probe tool's self-tests.
