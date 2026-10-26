# Test strategy

## Boundaries

| Suite | Real behavior | Isolated boundary / requirements |
|---|---|---|
| API Surefire | Info route, strict JSON contract and rejected writes (`InfoControllerTest`) | Standalone MVC, no DB/container needed |
| API Failsafe | Full Boot context/server, FlywayV1, PostgreSQL17 tables/columns/constraints, health and info HTTP (`FoundationIT`) | Testcontainers creates disposable real DB/random port. No H2 or skip without Docker. |
| Angular Karma/Jasmine | Shell/lazy routing/dashboard; typed connectivity decoding, loading/error/retry/cancellation | Real components/services; Angular HttpTestingController isolates HTTP transport, Chrome required |
| Playwright | Browser → dev proxy → live Boot → real migrated PostgreSQL; actual retry recovery and responsive status | Own API/web processes by default, caller starts configured Compose DB. Error injection mocks only the network boundary in named failure tests. |
| Python publisher regression | Exact issue bodies survive stdin publishing | Fake gh prevents real network writes |

No coverage percentage or load result is inferred from test count. Current narrow E2E does not imply authentication/business workflow coverage. New business modules need tests for transaction/authorization invariants and failures, not class-existence assertions or mock-only expectations.

## Standard commands

From repo root, Java21/Docker/Node22/Chrome available:

```bash
mvn -B -f apps/api/pom.xml clean verify
python3 -m unittest discover -s scripts/tests
cd apps/web
npm ci
npm run lint
npm test -- --watch=false
npm run build
npm audit
```

`mvn test` is useful for the DB-free boundary but cannot replace verify. Missing Docker must fail integration verification. Test-count discovery failures remain enabled.

## Live E2E

From root, configure `.env` per README; use only a trusted local env file, then:

```bash
docker compose config --quiet
docker compose up -d --wait db
set -a
source .env
set +a
export JAVA_HOME=$(/usr/libexec/java_home -v 21) # macOS example; other OS: select installed JDK21
cd apps/web
npm run e2e
```

Playwright uses installed Chrome and starts API8080 + Angular4200 on loopback. Ports must be free; it does not reuse unknown existing servers. It stops its process groups afterward and leaves the caller's DB/data intact. CI generates temporary random local credentials, starts its own DB and always tears that CI database down. No public deployment is needed.

Failures retain Playwright traces locally in ignored test-results. CI currently uploads no failure artifacts, so runner-local traces disappear when the runner is removed (TD-10). Do not upload traces containing secrets/private data; test fixtures are synthetic. On headless Linux install a supported Chrome if absent (GitHub Ubuntu runner includes it). Unit and E2E TypeScript must be checked, not merely transpiled.

## Before declaring done

Run relevant full suites on the actual tree, inspect failures and diff, verify actual PR checks on head, and record PASS/FAIL/BLOCKED with versions/commit. Add security/concurrency/migration upgrade scenarios when the corresponding feature exists. No automatic benchmark numbers or screenshot fabrication. Human acceptance/merge remains separate.

## Proposed identity acceptance (FD-009)

See [identity acceptance](../security/identity-acceptance.md). Eight current Python tooling tests (seven HTTP probe mechanics + existing publisher regression) are distinct from planned authentication/security tests. Proposed HTTP probes use loopback services/synthetic fixtures only and do not run as green product-security gates before the endpoints exist. Actual expiry/replay/logout/CSRF/tenant invariants remain unimplemented and require real Spring/PostgreSQL/Clock/browser tests after ADR review.
