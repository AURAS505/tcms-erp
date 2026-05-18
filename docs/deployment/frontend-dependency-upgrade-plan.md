# Frontend Dependency Upgrade Plan

Date: 2026-05-18

## Scope

This plan covered the remaining frontend npm audit findings from the stable TCMS ERP frontend. It was executed in Step 23J without using `npm audit fix --force`.

## Current Frontend Dependency Versions

Declared in `apps/frontend/package.json`:

- `next`: `^14.2.5`
- `react`: `^18.3.1`
- `react-dom`: `^18.3.1`
- `@tanstack/react-query`: `^5.51.1`
- `react-hook-form`: `^7.52.1`
- `zod`: `^3.23.8`
- `eslint`: `^8.57.1`
- `eslint-config-next`: `^14.2.35`
- `typescript`: `^5.5.4`
- `vitest`: `^2.0.5`
- `jsdom`: `^29.1.1`
- `tailwindcss`: `^3.4.7`

Resolved in the current local install/audit:

- `next`: `14.2.35`
- `eslint-config-next`: `14.2.35`
- `vitest`: `2.1.9`

## Vulnerabilities Summary

`npm audit` reports 10 vulnerabilities:

- 4 high severity.
- 6 moderate severity.
- 0 critical severity.

| Package area | Severity | Dependency chain | Suggested npm fix | Breaking |
| --- | --- | --- | --- | --- |
| `next` | High aggregate | direct `next` dependency, including nested `postcss` | `next@16.2.6` | Yes, major |
| `postcss` nested under `next` | Moderate | `next -> postcss` | `next@16.2.6` | Yes, major |
| `eslint-config-next` / `@next/eslint-plugin-next` / `glob` | High | direct `eslint-config-next -> @next/eslint-plugin-next -> glob` | `eslint-config-next@16.2.6` | Yes, major |
| `vitest` / `vite` / `vite-node` / `@vitest/mocker` / `esbuild` | Moderate | direct `vitest -> vite/vite-node/@vitest/mocker -> esbuild` | `vitest@4.1.6` | Yes, major |

## Why `npm audit fix --force` Is Deferred

The available fixes are major-version upgrades that can change framework behavior, build output, lint rules, test runtime behavior, and peer dependency expectations. Applying them in one forced command would combine several unrelated risks and make failures difficult to isolate.

Specific risks:

- Next.js 14 to 16 can affect App Router behavior, middleware, server components, production build output, and Docker image behavior.
- `eslint-config-next` 14 to 16 may require updated ESLint configuration and may remove or alter `next lint` assumptions.
- Vitest 2 to 4 can affect jsdom integration, module mocking behavior, Vite config compatibility, and test environment setup.
- React 18 is currently stable in this project; a Next.js 16 path may introduce peer pressure toward React 19 depending on the final selected version.

## Proposed Staged Upgrade Order

### Stage 1: Next.js Security Upgrade

Goal: remediate direct Next.js advisories and nested `postcss` advisories with the smallest safe Next.js upgrade path.

Tasks:

1. Review Next.js release notes for the latest secure version that supports the current app architecture.
2. Prefer the latest patched Next.js version compatible with the current React strategy.
3. Update `next` and the lockfile only.
4. Run the full frontend verification suite.
5. Build the production frontend Docker image if local Docker resources allow.

Verification:

```bash
cd apps/frontend
npm install
npm run lint
npm run typecheck
npm run test
npm run build
npm audit
```

Risk checkpoints:

- Middleware redirects and protected-route behavior.
- App Router page rendering.
- API base URL and CSRF handling.
- Production static generation output.

### Stage 2: ESLint and Next ESLint Config Upgrade

Goal: remediate `eslint-config-next` and transitive `glob` advisories.

Tasks:

1. Update `eslint-config-next` to the version aligned with the selected Next.js version.
2. Review whether `next lint` remains supported for the selected Next.js version.
3. If Next.js removes or changes lint command behavior, migrate to an explicit ESLint command in `package.json`.
4. Keep lint changes separate from application code changes unless rule fixes are required.

Verification:

```bash
cd apps/frontend
npm run lint
npm run typecheck
```

Risk checkpoints:

- `.eslintrc.json` compatibility.
- `next/core-web-vitals` config availability.
- CI lint command behavior.

### Stage 3: Vitest and Vite Tooling Upgrade

Goal: remediate Vitest/Vite/esbuild advisories without touching application runtime dependencies.

Tasks:

1. Update `vitest` to the selected secure major version.
2. Review `vitest.config.ts` compatibility for jsdom, globals, setup files, and alias resolution.
3. Update related test-only packages only if peer dependencies require it.
4. Keep test runtime changes isolated from Next.js runtime changes.

Verification:

```bash
cd apps/frontend
npm run test
npm run typecheck
```

Risk checkpoints:

- React Testing Library rendering behavior.
- jsdom version compatibility.
- Fetch/mock behavior in API-client tests.
- Path alias resolution for `@/*`.

### Stage 4: Final Audit and Production Verification

Goal: prove the dependency upgrade closed the audit findings without regressing the application.

Verification:

```bash
cd apps/frontend
npm audit
npm run lint
npm run typecheck
npm run test
npm run build
cd ../..
docker compose config --quiet
docker compose -f docker-compose.yml -f docker-compose.prod.yml config --quiet
docker compose -f docker-compose.yml -f docker-compose.prod.yml build frontend
```

Document:

- Vulnerabilities fixed.
- Vulnerabilities remaining, if any.
- Any compatibility changes required.
- Manual smoke test results for login, dashboard, financial pages, and protected routes.

## Rollback Strategy

1. Keep each stage in a separate commit.
2. If a stage fails, revert only that stage's commit.
3. Restore `apps/frontend/package.json` and `apps/frontend/package-lock.json` from the last passing commit.
4. Remove generated `.next/` output and reinstall dependencies:

```bash
cd apps/frontend
npm ci
npm run lint
npm run typecheck
npm run test
npm run build
```

5. Do not proceed to the next stage until the current stage is green.

## Recommended Future Upgrade Step

Execution result:

```text
docs/deployment/frontend-dependency-upgrade-result.md
```

Next recommended implementation step:

```text
STEP 23K - Final Release Verification After Dependency Upgrade
```