# Dependency Audit Report

Date: 2026-05-18

## Scope

This pass reviewed backend Python dependencies and frontend npm dependencies after the Step 23G pre-release verification. The goal was to identify security issues and apply only low-risk dependency remediations. No application features, accounting logic, financial workflow logic, or business rules were changed.

## Commands Run

Backend:

```bash
pip-audit --version
safety --version
python -m pip check
python -m pip list --outdated --format=json
python manage.py check
python -m pytest
python -m ruff check .
```

Frontend:

```bash
npm audit --json
npm audit fix
npm outdated --json
npm run lint
npm run typecheck
npm run test
npm run build
npm audit
```

Docker:

```bash
docker compose config --quiet
docker compose -f docker-compose.yml -f docker-compose.prod.yml config --quiet
```

## Backend Findings

- `pip-audit` was not available in the local environment.
- `safety` was not available in the local environment.
- `python -m pip check` reported no broken requirements.
- `python -m pip list --outdated --format=json` showed outdated packages in the local Python environment, but this environment contains many globally installed packages outside this repository's `apps/backend/requirements.txt`.
- No backend dependency changes were made because no repository-scoped automated vulnerability report was available and broad framework upgrades would be outside the low-risk scope of this pass.

## Frontend Findings

Initial `npm audit` reported 10 vulnerabilities:

- 4 high severity.
- 6 moderate severity.
- 0 critical severity.

Affected areas:

- `next`: multiple advisories affecting the installed Next.js 14 dependency tree.
- `eslint-config-next` / `@next/eslint-plugin-next` / `glob`: high severity advisory in the linting dependency chain.
- `vitest` / `vite` / `vite-node` / `@vitest/mocker` / `esbuild`: moderate severity development/test tooling advisories.
- `postcss`: moderate advisory in the nested Next.js dependency tree.

## Fixes Applied

Step 23J completed the controlled upgrade plan without `npm audit fix --force`:

- `next`: upgraded from `14.2.35` to `15.5.18`.
- `eslint-config-next`: upgraded from `14.2.35` to `15.5.18`.
- `vitest`: upgraded from `2.1.9` to `3.2.4`.
- `postcss`: pinned and overridden to `8.5.14` so Next's nested vulnerable PostCSS is not installed.

## Remaining Vulnerabilities

No npm audit vulnerabilities remain after Step 23J.

## Recommendation

Create a dedicated dependency upgrade step for:

1. Next.js and `eslint-config-next` major-version upgrade.
2. Vitest/Vite major-version upgrade.
3. Follow-up `npm audit` verification.
4. Full frontend test/build verification.
5. Production Docker image rebuild.

Recommended next review date: 2026-05-25, or earlier if the application is scheduled for internet-facing production deployment before then.

Detailed plan: `docs/deployment/frontend-dependency-upgrade-plan.md`.

Execution result: `docs/deployment/frontend-dependency-upgrade-result.md`.

## Status

Dependency audit completed and remediated for the frontend. Backend automated vulnerability tooling was unavailable in this environment, but `python -m pip check` passed.
