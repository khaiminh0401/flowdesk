# ADR-0002: Identity and session lifecycle

- **Status: Proposed — human review required; not implemented or approved**
- Date: 2026-10-26
- Issue: [FD-009 / #10](https://github.com/khaiminh0401/flowdesk/issues/10)
- Base: merged main `69ad007`, PR #18; no authentication/session/security filter exists there.
- Implementation prerequisite: explicit acceptance of this ADR and its linked contract. Merging an earlier foundation PR does not approve these policies.

## Context and alternatives

FlowDesk is a same-origin Angular SPA + single Boot/PostgreSQL modular monolith. M1 calls for login, recovery, logout, refresh rotation/reuse detection and later workspace isolation. There is no external resource-server/client requirement. These are proposed product/security defaults, not measured performance results.

| Option | Benefits | Costs and requirement fit |
|---|---|---|
| A: server-side authenticated HttpSession | Smallest Spring-native browser solution; central invalidation; HttpOnly cookie | Needs CSRF protection/shared session storage if scaled. No separate refresh-token rotation/replay mechanism; choosing it changes the stated M1 refresh requirement and requires explicit scope approval. |
| B: opaque access + rotating opaque refresh, DB-backed family (**recommended**) | Preserves rotation/replay requirement; immediate central revocation; no JWT signing/key lifecycle without an external consumer | DB authorization lookup and transactional rotation; tokens remain stateful; more code than A. Bounded M1 state, not a distributed auth platform. |
| C: signed JWT access + rotating refresh | Useful if independent resource servers must validate access without central lookup | Expired/stolen JWT remains usable unless revocation lookup is added; that erodes the claimed stateless benefit. Adds signing/issuer/audience/key rotation without a current need. |

**Proposal:** B. If the reviewer prefers minimum browser-session complexity over the explicit refresh objective, accept A only with an updated M1 scope/contract. JWT is not selected; no JWT validation/signing feature is claimed. Reconsider C only for a concrete independent resource-server requirement and reviewed ADR.

## Proposed policy defaults to approve

| Concern | Proposed rule |
|---|---|
| Provisioning | First slice has no public registration/reset/MFA. Synthetic local/test users provisioned through a reviewed development-only fixture command; no account-creation HTTP backdoor, hardcoded password or automatic production seed. Real onboarding must be specified before public release. |
| Passwords | Argon2id, initial memory 19,456 KiB, iterations 2, parallelism 1; Spring encoder + its required crypto provider, encoded parameters/salt per hash, rehash on successful login when policy changes. No fabricated latency claim; measure before production. |
| Input | Password15–128 Unicode code points, preserved exactly (no trim/case/normalization); no truncation. Email ASCII for initial slice, trim and lowercase consistently; request body limited to 8 KiB before password work; larger payloads return413. Unicode limits require code-point-aware validation on both Java and Angular, not mismatched UTF-16 length assumptions. Unknown account and wrong password use generic 401 and one equivalent Argon verification path, not a timing guarantee. |
| Login throttling | Proposed temporary limits: 5 failed attempts per normalized account/15min and20 per client IP/15min, applied to existing and nonexistent accounts alike;429+Retry-After. No permanent lockout. Bounded in-memory limiter for one API instance; trust forwarded IP only from explicitly trusted ingress. Review DoS trade-off before public release. |
| Token material | Independent CSPRNG 32-byte values, base64url; raw access exists only in response/client memory, raw refresh only in HttpOnly cookie. Store SHA-256 token hashes, never raw values, in DB. No signing key is needed for high-entropy opaque tokens. |
| Access lifetime | 10 min from issuance; evaluate `now >= expires_at` as expired. Every protected request checks token expiry, active family, user enabled and family absolute/idle expiry. No persisted token/role snapshot is authoritative for workspace permission. |
| Refresh lifetime | Family absolute7 days; idle 24 h since last successful refresh; replacements never extend the absolute deadline. Each refresh is single-use; consumption and replacement commit atomically. |
| Replay | A recognized consumed refresh token revokes its whole family and all associated access tokens, then returns the same generic 401 as invalid/expired refresh. Invalid CSRF/origin is rejected before token consumption/revocation. Other families/devices remain active. |
| Concurrent refresh | Exactly one consumption can succeed; a duplicate is treated as replay and revokes the family, including the winner's newly issued tokens. No replay grace window. This can force legitimate multi-tab clients to sign in again; it is an explicit trade-off, not a promise that both calls succeed. |
| Logout | Normally idempotent204 after valid CSRF/origin: revoke the family selected by a usable credential and clear refresh/CSRF cookies. Expired/malformed/unknown bearer is ignored when a usable refresh is present (and vice versa); neither usable still204. Exception: two usable credentials for different families return generic401, clear refresh cookie, and revoke neither. Missing/invalid CSRF remains403. No family/token reason is exposed. |
| Transport/cache | Production HTTPS, same-origin only, no wildcard CORS; Cache-Control:no-store on auth responses, never tokens in URLs. Development insecure cookies require an explicit loopback-only profile, not an automatic production fallback. |

Parameter values are proposals to review; do not implement them merely because this file exists.

## Cookies and CSRF: use the framework, not custom double-submit crypto

Production refresh cookie: `__Host-FD-REFRESH`, Secure, HttpOnly, SameSite=Strict, Path=/, no Domain. It is read only by refresh/logout; it **never** authenticates `/me` or business APIs. Local loopback-only profile uses `FD-REFRESH`, no Secure, otherwise same rules. SameSite is defense in depth, not the CSRF control.

Use Spring Security's **HttpSessionCsrfTokenRepository** for CSRF state and coherent request-token handling. The servlet session holds only CSRF state, not an authenticated SecurityContext or a saved login request. Configure nonpersisting security-context handling (for example NullSecurityContextRepository), disable saved-request/form-login/basic fallbacks, authenticate each bearer request independently and clear thread-local context after it. Do not use a stateless setting that accidentally disables the required CSRF session. Its production cookie `__Host-FD-CSRF` is Secure/HttpOnly/SameSite=Strict/Path=/, no Domain; local cookie `FD-CSRF`. CSRF state uses a20 min idle servlet-session lifetime. No new Spring Session/shared-store dependency is required for the current single-process proposal; restart loses CSRF state and the browser reboots it. Before multiple replicas, review shared CSRF state or routing instead of silently relying on node-local sessions.

`GET /api/v1/auth/csrf` returns the framework-issued request token with header name `X-CSRF-TOKEN`, creates CSRF state if absent and uses no-store. Angular keeps it in memory and submits it on **every unsafe same-origin request**, including login, refresh and logout. Do not replace the synchronizer token with a simple attacker-injectable readable cookie. Preserve framework token masking/BREACH handling; prove the returned token round-trip with real HTTP tests rather than guessing its encoding.

All unsafe browser commands also require an exact configured `Origin`; reject missing/mismatching/null origins with403. Derive allowed origin from explicit deployment config, never arbitrary Host/X-Forwarded-* headers. Local proxy origin is the frontend4200 origin; it is not automatically the backend8080 origin. No cross-origin credentialed access is part of this proposal. Native clients are outside this first slice.

Login rotates the CSRF servlet-session identifier and invalidates its previous token after authentication success. Logout invalidates it. Angular fetches a fresh CSRF token afterward. A stale/missing CSRF state returns 403 `CSRF_INVALID` **before side effects**; bootstrap/retry at most once is permitted for this code. A403 authorization failure must not trigger refresh or automatic replay. Bound anonymous CSRF-session creation/rates and storage before public exposure; production hardening/release is not implied by a local demo.

## Server storage and transaction design (proposed V2, not a migration)

V1 stays immutable. Proposed identity-owned tables:

- `user_credentials`: user_id FK/PK to app_users, encoded password hash, disabled_at. Add normalized-email uniqueness with a lower(email) unique index; migration must fail on preexisting case-colliding accounts for explicit resolution, never silently merge identities.
- `session_families`: UUID id/user_id FK, created_at, absolute_expires_at, last_refreshed_at, revoked_at and internal reason.
- `refresh_tokens`: UUID id, family_id FK, unique 32-byte token_hash, issued_at/expires_at, consumed_at and replacement_id. Retain consumed hashes until family expiry to detect replay; cleanup cannot erase a live replay tombstone.
- `access_tokens`: unique 32-byte token_hash, family_id FK, issued_at/expires_at. Family/user state is checked centrally; family revocation need not update every access row for correctness.

Login creates family/access/refresh atomically after password verification. If the browser presents a recognized existing refresh credential, successful login also revokes that previous browser family in the same transaction before replacing its cookie; failed login leaves the previous family intact. This defines account-switch behavior and avoids silently orphaning an active browser family. Other device families are not revoked. Rotation finds hash, locks family row, re-reads token under that lock, checks user/family/token deadlines, consumes old token and inserts replacement/access in one transaction. All code paths lock family before dependent token rows. Return a typed result from the transaction; map a replay result to401 **after revocation commits**. Throwing an unchecked authentication exception inside the revocation transaction must not roll back the security side effect. Cookie/HTTP success is emitted only after commit; DB failure yields503 without partial persisted rotation.

Unknown/random token does not reveal a family and causes no arbitrary revocation. Expired/disabled families never issue replacements. Logout/replay and protected mutations serialize on family state when the command needs a strict no-write-after-revocation guarantee. An already authorized read may complete; logout cannot retract bytes already delivered.

### Logout credential resolution

After CSRF/origin succeeds, optional logout credential resolution applies **before** any family mutation. A bearer is usable only when unexpired and its user/family is active. A refresh is usable when its hash is recognized, family/user and refresh deadlines are valid; a consumed-but-otherwise-live refresh identifies that same family for revocation only, never a new token. Expired/malformed/unknown credentials are ignored. Two usable credentials for distinct families cause generic401/no revocation; if only one is usable revoke that family and204; neither usable still204. Cookie clearing follows the contract. Auth-path handling must not reject an invalid optional bearer before these logout rules run; this exception does not weaken protected-resource bearer authentication or CSRF checks.

## Angular lifecycle

Access and CSRF tokens only in memory; no localStorage/sessionStorage/IndexedDB, URL or logs. Startup bootstraps CSRF then makes at most one refresh attempt using HttpOnly cookie; failure ends in signed-out state. Login success installs access response and fetches fresh CSRF before the next unsafe request. Interceptor applies only to same-origin `/api/` requests, excludes auth refresh/login recursion, never external URLs.

On protected401, coordinate one refresh in the tab, then retry the original request at most once only if server authentication rejected it before business effects. Retried unsafe commands must preserve a stable request/idempotency key where the domain contract requires it. Network timeout is ambiguous and is not automatically replayed. On failed recovery/logout/replay: clear memory identity and show sign-in. Do not refresh on business403/404.

Tabs coordinate refresh where possible without persisting/broadcasting raw tokens; hard duplicate races still cause reauthentication under the explicit replay rule above. This bounded policy sacrifices seamless multi-tab recovery for strict single-use semantics. Revisit only with a reviewed concurrency design, not a hidden replay grace period.

## Workspace authorization ownership (FD-011/#12)

Identity supplies authenticated user/family IDs; workspace owns membership/roles. No workspace/role claim supplied by a client or cached token grants authority. Scope repository reads and writes by server-validated workspace + actor. Absent/cross-tenant resource returns404; known same-workspace action denied by role returns 403; unauthenticated returns 401.

For protected mutations, authorization and write share an application transaction: family shared lock → membership shared lock → domain locks in documented order. Revocation/role changes take conflicting locks. A command may commit before revocation completes; a command ordered after completed revocation must be denied. Tests must exercise that ordering, not assert an impossible retroactive undo. Final-owner/ownership-transfer rules require a separate reviewed workspace matrix; no workspace tables/endpoints are implemented here.

## Error/logging rules

See proposed OpenAPI. Generic401 for login; generic 401 `SESSION_INVALID` for all refresh invalidity/replay outcomes.403 for CSRF/origin,429 for throttling, safe503 for store unavailability. No redirects/HTML login page for JSON APIs. Error body has type/title/status/code/requestId only; no exception/SQL/email/account-existence or token reason.401 from protected APIs is authentication failure before domain effects, not a blanket catch for business errors.

Security events record event type, time, opaque request ID, internal actor/family ID when known, outcome and internal reason without passwords/hashes/tokens/CSRF/cookies/Authorization or raw request bodies. Rate-limit storage may use a keyed identifier; do not log raw credential identifiers or arbitrary headers. Do not add full immutable business audit infrastructure solely for login logging.

## Acceptance and rollout

[Threat model](../security/identity-threat-model.md), [proposed OpenAPI](../api/identity-session.proposed.json), [acceptance scenarios and probe](../security/identity-acceptance.md). These do not certify a working security mechanism. Phase1 implementation is #11 after explicit review; workspace tests join #12, not a fake current tenant implementation. Keep existing public info/aggregate health endpoints and tests intact. No deploy/public exposure or destructive migration is authorized by this proposal.

## Review decisions still outstanding

1. Accept B with rotation/replay complexity and strict concurrent-tab reauthentication, or explicitly reduce scope to A?
2. Accept lifetime/input/throttle/cookie/origin defaults above for the initial same-origin browser slice?
3. Accept development-only account provisioning and no public registration/reset/MFA in that slice?

**Approval record: none.** Record the human review reference/date and any changes before marking this ADR Accepted or changing runtime security policy.

## Sources checked

Design is a project proposal informed by [OWASP session management](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html), [password storage](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html), [CSRF prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html) and [Spring Security6.5 CSRF](https://docs.spring.io/spring-security/reference/6.5/servlet/exploits/csrf.html). Specific expiry/rate/input choices are proposed FlowDesk policy, not values mandated by these sources.
