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

`npm audit` reported 10 vulnerabilities:

- 4 high severity.
- 6 moderate severity.
- 0 critical severity.

Affected areas:

- `next`: multiple advisories affecting the installed Next.js 14 dependency tree.
- `eslint-config-next` / `@next/eslint-plugin-next` / `glob`: high severity advisory in the linting dependency chain.
- `vitest` / `vite` / `vite-node` / `@vitest/mocker` / `esbuild`: moderate severity development/test tooling advisories.
- `postcss`: moderate advisory in the nested Next.js dependency tree.

## Fixes Applied

No dependency version changes were applied.

`npm audit fix` was run without `--force`. It did not resolve the remaining vulnerabilities because npm only offered breaking major upgrades:

- `next@16.2.6`
- `eslint-config-next@16.2.6`
- `vitest@4.1.6`

The temporary lockfile normalization produced by `npm audit fix` was reverted because it did not remediate vulnerabilities and was unrelated to a safe dependency upgrade.

## Remaining Vulnerabilities

The npm vulnerabilities remain unresolved in this pass.

Reason for deferral:

- The available remediation paths require major framework/tooling upgrades.
- Upgrading Next.js from 14 to 16 can affect App Router behavior, middleware, build output, lint integration, and deployment compatibility.
- Upgrading Vitest from 2 to 4 can affect test runtime behavior and configuration.
- These upgrades need a dedicated compatibility ticket with full frontend, backend integration, Docker production build, and manual smoke verification.

## Recommendation

Create a dedicated dependency upgrade step for:

1. Next.js and `eslint-config-next` major-version upgrade.
2. Vitest/Vite major-version upgrade.
3. Follow-up `npm audit` verification.
4. Full frontend test/build verification.
5. Production Docker image rebuild.

Recommended next review date: 2026-05-25, or earlier if the application is scheduled for internet-facing production deployment before then.

Detailed plan: `docs/deployment/frontend-dependency-upgrade-plan.md`.

## Status

Dependency audit completed and documented. No safe low-risk dependency remediations were available through non-forced tooling in this environment.
