# Security model: implemented boundaries and M1 review

## Current facts

Baseline main has no authentication, session, refresh token, role, workspace ownership or protected business API. `InfoController` returns application/stage; Actuator exposes aggregate health/info. Browser status uses only these public diagnostic fields and rejects malformed/unhealthy responses. It never displays raw HTTP error bodies. No credentials/cookies/tokens or permissive CORS rule is added by connectivity.

DB credentials are exported from ignored `.env` for local API startup. Compose binds DB to loopback. README explicitly binds API to loopback; `application.yml` does not enforce a deployment bind address. Do not publish this API as a secure product service. SQL V1 uses constraints and integration tests; that is not tenant isolation.

Dependency evidence: npm audit is run against the lockfile and recorded per session. GitHub Dependabot alert retrieval failed with403 (disabled/scope); no backend vulnerability assessment is claimed. Tests, a green badge or a clean regex scan do not establish a comprehensive security audit.

## Required M1 design review (#10)

Before changing security policy, document and obtain review of:

- Identity provisioning, password hashing/work factor and upgrade behavior; synthetic seed strategy with no real credentials.
- Generic login failures, validation, brute-force policy and audit/log redaction; no password/hash/token in responses or logs.
- Session model choice: server session versus access/refresh tokens; lifetime, expiration and revocation; JWT issuer/audience/algorithm/key rotation if JWT is chosen.
- Refresh rotation and reuse detection if refresh tokens are used: atomic rotation, token hashing, replay revocation, race/multi-tab behavior.
- Storage and transport: HTTPS, HttpOnly/Secure/SameSite/path policy, XSS exposure, CSRF protection for cookie-authenticated commands, same-origin deployment routing. Do not disable CSRF solely to make tests pass.
- Logout semantics: server invalidation plus browser state cleanup; session recovery must not resurrect revoked sessions.
- Workspace permission matrix: authenticated actor + explicit workspace scope, deny by default, IDOR/BOLA, privilege escalation, last-owner rules and concurrent membership changes.

These are requirements to specify/test, not an accepted token policy or implemented controls. Proposed RFC/ADR must remain marked proposed until reviewed. Angular guards only improve UX; every business authorization decision must be server-side.

## Required evidence with implementation

Real PostgreSQL integration tests must prove wrong/expired/revoked credentials and replay outcomes; authenticated users cannot read or mutate another workspace by substituting IDs; privilege changes and concurrency preserve invariants. Browser tests cover login/recovery/logout and safe failure states. Security-specific logging tests check that sensitive data is omitted. Match test cases to the accepted contract rather than relying on framework defaults.
