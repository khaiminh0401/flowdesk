# Contributing

- Work on short-lived branches named `feat/FD-xxx-description`, `fix/FD-xxx-description`, or `docs/FD-xxx-description`.
- Use Conventional Commits, e.g. `feat(project): add create project endpoint`.
- Keep each PR scoped to one issue, with tests and updated documentation when appropriate.
- Never commit secrets, production data, internal assets or credentials.
- Do not merge PRs when required checks fail.

## Required checks

Use JDK 21, Maven 3.9+, Node 22.12+ (22.x), npm 10+, Docker and Chrome. Run the README verification commands before requesting review. A unit-only Maven run is useful locally but does not satisfy integration acceptance. Do not add Docker-unavailable skips or H2 fallbacks. Keep `.env` out of commits and use `npm ci` with the committed lockfile.

Describe tested commands, failures/blockers and trade-offs in the PR. Keep the PR draft until required checks pass. Do not close Sprint 0 issues until each acceptance criterion has evidence; references alone do not imply completion. Add a new Flyway migration instead of editing one that has already run.
