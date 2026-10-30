# Current state / resume here

Snapshot: 2026-10-30. Manual handoff; not automatically synchronized with GitHub. Fetch remote refs and inspect actual issues/PRs/checks before resuming.

## Base and active work

- M0 foundation/connectivity is merged on main `69ad007` through [PR #18](https://github.com/khaiminh0401/flowdesk/pull/18); historical main [CI40338793703](https://github.com/khaiminh0401/flowdesk/actions/runs/40338793703) passed.
- Active M1 **design** is [FD-009/#10](https://github.com/khaiminh0401/flowdesk/issues/10), branch `docs/FD-009-identity-session-design`, [draft PR #19](https://github.com/khaiminh0401/flowdesk/pull/19) targeting main. Clean working tree at session start, head `4fbb61f`; remote main is unchanged after fetch. PR19 remains unmerged; all 16 issues remain open across the seven milestones. No duplicate issue/PR was created or issue closed.
- No application authentication, credential model, session/refresh logic, RBAC or workspace domain exists. ADR-0002 and its API/threat/acceptance documents remain **Proposed**. No human approval is recorded in GitHub comments/reviews or this session.

## Implemented this session

Fresh review discovery found [hostname routing comment](https://github.com/khaiminh0401/flowdesk/pull/19#discussion_r4378795019) on PR19 after the previous handoff. Corrected the existing probe/tooling increment rather than starting dependent runtime identity work:

- Accept only literal `127.0.0.1` / `[::1]` bases; reject `localhost` and DNS names before any credential request. Normalize URL scheme so HTTPS selects the intended cookie profile. Existing no-proxy/no-redirect controls remain.
- Preserve cookie-jar domain/path/Secure/expiry filters before overriding the selected synthetic refresh token; keep stored refresh state unchanged by the override itself.
- Share exact top-level TokenResponse/access-token checks between login and refresh. Replay first proves replacement bearer access succeeds, then checks that the same bearer is denied after replay. This prevents empty/malformed or never-working tokens from becoming false revocation evidence.
- Added seven regression tests, including controlled resolver/local HTTP sentinel and cookie/response/replay observations. Total Python tooling suite: 15 (14 probe mechanics + publisher regression). These are not product-authentication tests or a full schema/browser-security validator.

Independent reviewer found no Critical/Important/Minor issue in the two-file code/test diff against `4fbb61f` and independently reran the 15 tests. Remaining proposal review concerns are recorded in PROJECT-INTELLIGENCE/TECHNICAL-DEBT: login/account-switch refresh-cookie read scope and explicit OpenAPI logout/error/header/input constraints need reconciliation during design review. Automated review does not approve policy.

## Fresh local verification

Environment: JDK21.0.9 selected explicitly (shell default JDK25 is unsuitable), Maven3.9.12, Node22.18.0, npm10.9.3, Docker29.4.0, Chrome156.

| Command / evidence | Result |
|---|---|
| `python3 -m unittest discover -s scripts/tests -v` | PASS, 15 tests; new behavior observed failing before fixes |
| Java21 `mvn -B -ntp -f apps/api/pom.xml clean verify` | PASS, 2 unit +7 real PostgreSQL Testcontainers IT; zero failures/errors/skips |
| `npm ci` in apps/web | PASS, locked dependencies installed |
| `npm run lint` | PASS, zero warnings allowed |
| `npm test -- --watch=false` | PASS, 18 Chrome tests |
| `npm run build` | PASS, production bundle |
| `npm audit` | PASS, zero reported vulnerabilities for frontend dependency tree only |
| `docker compose config --quiet`; configured local DB health | PASS |
| Java21 + local env `npm run e2e --prefix apps/web` | PASS, 4 live browser/proxy/API/PostgreSQL scenarios |
| Diff whitespace / secret-pattern review | PASS before commit; synthetic fixtures only |
| GitHub Dependabot alerts | BLOCKED, endpoint403: alerts disabled / insufficient scope; backend CVEs remain unverified |

Playwright emitted the existing Node NO_COLOR/FORCE_COLOR warning; tests still passed. No CI gate/dependency/runtime policy/migration was changed. Local verification logs and browser artifacts are ignored, not committed. This session started the existing configured loopback DB only for live checks, then restored its stopped state without deleting data. No public deployment or permission widening.

Delivered code/documentation commit `6948be0` to existing draft PR19. Fresh [CI41015107926](https://github.com/khaiminh0401/flowdesk/actions/runs/41015107926) on that exact commit passed api/web/e2e; logs confirm 9 backend,15 tooling,18 Angular and4 live browser tests. This final handoff-only update records that verified commit; check the actual final PR head before accepting. GitHub annotations report Node20 action-runtime deprecation (runner forces Node24), setup-java v4 deprecation and ubuntu-latest image migration; tracked as TD-11, no workflow changes bundled.

## Next task and human review boundary

Review [ADR-0002](../adr/0002-identity-session-lifecycle.md), threat model, proposed OpenAPI and outstanding design clarifications in PR19. `AGENTS.md`: “Stop for human review before security-sensitive policy changes”. Approve or revise model B, cookie/CSRF/lifetime/password/throttle defaults, strict duplicate-refresh reauthentication, and development-only provisioning. User decision in this session (2026-10-30): “Keep pending; review PR #19 first”. Policy remains unapproved; do not begin runtime identity implementation or infer approval from generic autonomous-execution instructions.

After explicit approval, record its date/reference and reconcile the design concerns before planning FD-010/#11 as small end-to-end increments with real PostgreSQL/browser security acceptance. Never assume PR19 is merged on main. FD-011/#12 follows merged identity and a reviewed workspace permission matrix. Never merge or force-push automatically.

## Historical evidence retained

2026-10-26: actual proposed anonymous probe on temporary loopback18080 returned FAIL (expected401, received404); lifecycle was BLOCKED without synthetic credentials. The app has not gained identity endpoints since. Earlier proposal/probe commits `5f15507`, `2bd1293`, `0fe31c6`, `cd0c454`, `4fbb61f` and their CI are historical evidence, not human acceptance or fresh security verification. TD-03 (no entity mappings), TD-10 (no CI failure-artifact upload), backend scanner coverage and all future business acceptance remain explicit limitations.
