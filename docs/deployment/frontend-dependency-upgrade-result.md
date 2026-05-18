# Frontend Dependency Upgrade Result

Date: 2026-05-18

## Summary

The staged frontend dependency upgrade completed successfully. The npm audit baseline was reduced from 10 vulnerabilities to 0 vulnerabilities without using `npm audit fix --force`.

No backend code, accounting logic, business workflows, or UI behavior was changed. The only source compatibility change was updating dynamic App Router detail pages to the Next.js 15 async `params` contract.

## Packages Upgraded

| Package | Before | After | Reason |
| --- | --- | --- | --- |
| `next` | `14.2.35` | `15.5.18` | Resolves high-severity Next.js advisories while retaining React 18 compatibility. |
| `eslint-config-next` | `14.2.35` | `15.5.18` | Resolves transitive `glob` advisory in the Next ESLint plugin chain. |
| `vitest` | `2.1.9` | `3.2.4` | Resolves Vite/esbuild test-tooling advisories with the smallest safe major upgrade. |
| `postcss` | `8.5.14` direct, `8.4.31` nested under Next | `8.5.14` direct and overridden | Resolves the remaining nested Next.js PostCSS advisory. |

## Audit Result

Before:

- 10 vulnerabilities.
- 4 high severity.
- 6 moderate severity.

After:

- 0 vulnerabilities.

## Compatibility Changes

Next.js 15 expects dynamic App Router `params` to be promise-like in generated route types. The affected client detail pages now unwrap `params` with React `use(params)`, and direct page tests pass `Promise.resolve({ id })`.

Affected area:

- Dynamic dashboard detail routes under `apps/frontend/app/dashboard/**/[id]/page.tsx`.
- Tests for directly rendered dynamic detail pages.

## Commands Run

```bash
cd apps/frontend
npm audit
npm install next@15.5.16
npm install next@15.5.18
npm install -D eslint-config-next@15.5.18
npm install -D vitest@3.2.4
npm install
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

## Final Verification

- `npm audit`: passed, 0 vulnerabilities.
- `npm run lint`: passed. Note: `next lint` is deprecated and should be migrated before Next.js 16.
- `npm run typecheck`: passed.
- `npm run test`: passed, 189 tests.
- `npm run build`: passed.
- `docker compose config --quiet`: passed.
- `docker compose -f docker-compose.yml -f docker-compose.prod.yml config --quiet`: passed.

## Remaining Issues

No npm audit vulnerabilities remain.

Operational follow-up:

- Migrate from `next lint` to the ESLint CLI before upgrading to Next.js 16, because Next.js 15 warns that `next lint` will be removed in Next.js 16.

## Status

Frontend dependency upgrade completed successfully and is ready for release verification.
