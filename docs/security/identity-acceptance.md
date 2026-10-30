# Identity acceptance specification — proposed, not passing product tests

FD-009/#10 defines testable behavior for [ADR-0002](../adr/0002-identity-session-lifecycle.md) and the separate [proposed OpenAPI](../api/identity-session.proposed.json). Nothing here means authentication, refresh rotation or workspace isolation exists on main69ad007. No production migration/filter/endpoint is added by this design PR.

## Executable HTTP probes

`scripts/security/verify_identity_contract.py` uses only Python standard library, accepts only literal `127.0.0.1` / `[::1]` base URLs (no `localhost` or DNS names), ignores system proxies, never follows redirects and withholds response bodies/credential values from output. It makes real HTTP requests; it does not simulate a secure server. It does not belong in the current product green gate, because the proposed endpoints do not exist yet. Probe-tool self-tests run in the existing Python CI suite; those tests prove tool behavior, not FlowDesk security.

After the corresponding implementation and synthetic fixtures exist, start the API + proxy using README instructions:

```bash
python3 scripts/security/verify_identity_contract.py --base-url http://127.0.0.1:4200 --case anonymous
# Provide AUTH_PROBE_EMAIL and AUTH_PROBE_PASSWORD through the local shell/secret input,
# using synthetic provisioned users only; never commit values or enable shell tracing.
python3 scripts/security/verify_identity_contract.py --case lifecycle
python3 scripts/security/verify_identity_contract.py --case replay
# Expiry: additionally provide AUTH_PROBE_EXPIRED_ACCESS / AUTH_PROBE_EXPIRED_REFRESH.
python3 scripts/security/verify_identity_contract.py --case expiry
# FD-011 only: provide AUTH_PROBE_OWN_RESOURCE / AUTH_PROBE_OTHER_RESOURCE paths
# to existing resources in two different workspaces, then:
python3 scripts/security/verify_identity_contract.py --case workspace
```

Origin is the selected proxy base URL; use the configured frontend origin, not a different backend origin. Never run against real accounts: replay/logout probes deliberately revoke the synthetic account's family. Each case uses independent cookie-jar state. Refresh overrides retain domain/path/Secure/expiry filtering for other cookies; this HTTP tool does not enforce browser-only HttpOnly/SameSite rules or certify cookie flags. Login and refresh check the exact top-level TokenResponse fields and opaque access-token shape; this is not a full OpenAPI response validator. Exit0 = selected HTTP observations passed,1 = observed contract mismatch,2 = unavailable local service/required fixture. No response body, token, password or cookie value is printed or persisted.

| Probe | Observations / limits |
|---|---|
| anonymous | /me401; bootstrap CSRF200; missing CSRF and wrong Origin403; unknown account with CSRF returns generic401. Does not prove timing/rate/known-account equivalence. |
| lifecycle | Valid login, bearer /me200; cookies alone /me401; logout204, old access401, repeated CSRF-protected logout204. |
| replay | Login → refresh200 → replacement bearer /me200 → replay consumed token401 → same replacement bearer /me401. Confirms externally visible family revocation; integration test must additionally inspect committed DB state. |
| expiry | Prepared expired access/refresh rejected401. Fixtures must belong to previously valid, otherwise active families. HTTP alone cannot prove exact-time comparisons or distinguish expiry from other denial. |
| workspace | Actor can read their known resource200, same actor receives404 for another tenant's known existing resource. Partial read-isolation evidence only; not a replacement for write/role/concurrency tests. |

Expiry fixture preparation is an **internal test fixture**, not a public clock/token-minting endpoint. FD-010 tests inject a controlled Clock into the identity service and seed hashed synthetic token values/deadlines into a disposable Testcontainer. FD-011 supplies two real workspace memberships/resources. Neither fixture capability is implemented here. Missing fixture is BLOCKED, not a skipped/passing security assertion.

## Required implementation scenarios

Each row is an acceptance requirement with a concrete arrange/action/assert sequence. JUnit/Playwright implementations belong to FD-010/#11 or FD-011/#12 after policy review. The HTTP probes cover only the explicitly listed subset.

| ID | Arrange → action → required observation | Required driver |
|---|---|---|
| I-01 | Unknown email and existing email/wrong password, valid CSRF/origin → login → identical generic401 code/shape, no account existence/hash details, no new family | Real Boot/PostgreSQL HTTP + log capture; anonymous probe covers unknown case only |
| I-02 | Disabled user's valid credentials → login → same generic401; old access denied and refresh issues no replacement | Real PostgreSQL integration |
| I-03 | Existing and unknown account buckets just below limit → failed login to threshold → both temporary429+Retry-After on next attempt; after controlled window permit verification; IP threshold, oversize/malformed body and bounded hash work also exercised | Injected Clock + real filter/service HTTP; no fabricated timing threshold |
| I-04 | Same valid synthetic password stored for two users → persisted salted Argon2id hashes differ, neither equals plaintext, correct verification succeeds, wrong one fails; configured old parameters rehash on valid login | Encoder/application + DB assertions |
| I-05 | Pre-login CSRF session and valid user → successful login → new family and different CSRF session ID; injected pre-login identity state never authenticates /me; access only in JSON, refresh only cookie | Real HTTP/cookie integration + browser |
| I-06 | Valid login → attempt unsafe action with prior CSRF →403 and no mutation; fresh csrf bootstrap token then passes; expiry/restart creates fresh CSRF state, never disables validation | Real filter HTTP + restart/state test |
| I-07 | Active family/refreshR0 → valid rotation → one consumedR0, one replacementR1, accessA1; old token not reusable; deadlines do not exceed family absolute expiry | Transactional PostgreSQL assertions + replay probe subset |
| I-08 | Two independent transactions submit identicalR0 with valid CSRF → at most one rotation initially succeeds; duplicate triggers generic401 and committed family revocation; even winner's returned access denied afterward; other families unaffected | Synchronized real PostgreSQL concurrent test, not sequential mocks |
| I-09 | ConsumedR0 recognized → replay →401 only after revocation commits; fresh transaction sees revoked family and newest access rejected. Force a rotation DB failure →503, no partially consumedR0/replacement/access | Real transaction rollback/failure-injection integration |
| I-10 | Controlled now at access deadline−1ns, equal and+1ns, active family → accept before, reject at/after. Independently test idle24h and absolute7day family boundaries with otherwise valid access/refresh | Injected Clock + real DB; expiry probe observes prepared expired values only |
| I-11 | Active family → logout commits → all later requests with its access denied; other family still works; repeated logout204 after fresh CSRF; no tokens still204 with valid CSRF | Real HTTP/DB + lifecycle probe |
| I-12 | Valid refresh with missing/wrong CSRF or Origin →403, refresh remains unconsumed and family active; same token with valid CSRF/origin still rotates. Simple cross-site form rejected before password/token work | Filter integration + browser controlled-origin test |
| I-13 | HTTPS profile cookie response → assert __Host names/Secure/HttpOnly/Strict/Path=/ and no Domain; loopback profile explicit alternate names; refresh/CSRF cookies alone never grant resource identity | HTTP cookie assertions + browser context; lifecycle covers cookie-only denial |
| I-14 | Startup/login401/recovery/logout and two concurrent requests → at most one refresh per tab, at most one original retry; no bearer on external URL; business403 and ambiguous network timeout never auto-replayed; client XSS string renders as text | Angular HttpTestingController + browser; never assume guards enforce security |
| I-15 | Sentinel synthetic credentials/CSRF/body → all failure/success paths and captured logs/traces → no plaintext/hash/tokens/cookies/Authorization/email/body leak; only safe problem fields; auth responses no-store | Log capture/strict contract/browser storage assertions |
| I-16 | Two usable credentials for familyA/B → logout401/no revocation. Valid refreshB + expired/malformed/unknown bearer →204/B revoked. Valid bearerA + invalid refresh →204/A revoked. Neither usable →204; missing CSRF still403 in every branch; fresh login never adopts an attacker-supplied family | Real integration through actual filters (no optional-bearer early rejection) |
| I-17 | Store unavailable before commit → safe503 and no token issue; CSRF state lost after restart →403, fresh bootstrap then valid flow; no server-authenticated SecurityContext survives in CSRF session | Real failure/restart integration |
| I-18 | Cleanup runs while old refresh consumed but family unexpired → replay tombstone retained; expired family cleanup removes descendants in bounded batches without invalidating active unrelated family; anonymous CSRF session growth bounded | PostgreSQL cleanup + load-bound test; implementation/release values reviewed |
| I-19 | Browser already has familyA → successful account switch/login → new familyB and old browser familyA revoked atomically; failed login leaves A active; independent device familyC remains active | Real integration + browser |
| W-01 | Alice owns resourceA, Bob owns existing resourceB in distinct workspaces → Alice substitutes workspace/resource ID on read AND update/delete →404 and B unchanged; own allowed operation succeeds | FD-011 real PostgreSQL + browser; workspace probe read subset |
| W-02 | Member role lacks member-admin action in same workspace →403/no mutation; client-supplied admin role/workspace claim ignored; last-owner rule validated under concurrent changes | FD-011 permission matrix + concurrency tests |
| W-03 | Command holds shared family/membership lock, revoke/role-change competes → command ordered before revoke can finish; command after revoke commit denied. Reverse start order and assert no unauthorized later write; consistent lock order prevents deadlock | FD-011 synchronized transactions and row-state assertions |

## Current evidence and review gate

- Probe-tool tests: run `python3 -m unittest discover -s scripts/tests`; no auth service is mocked into a false product PASS.
- Current main/proposed runtime probes: expected mismatch (endpoints absent) or unavailable-fixture BLOCKED. Do not disable assertions or run these as green product checks until their prerequisites exist.
- Actual behavior acceptance for I/W scenarios remains **NOT IMPLEMENTED / NOT VERIFIED**. Human policy approval remains **PENDING**. A green docs/tool CI validates existing product regression and probe mechanics only.
