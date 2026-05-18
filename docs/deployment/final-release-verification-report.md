# Final Release Verification Report

Date: 2026-05-18

## Summary

Final release verification was completed after the frontend dependency upgrade. The frontend npm audit remains clean with 0 vulnerabilities. Backend checks, frontend checks, Docker Compose config validation, production image builds, production-like container startup, migrations, health endpoints, and smoke checks were completed.

One compatibility fix was required during this pass: dynamic Next.js 15 dashboard detail routes no longer rely on React `use(params)`. They now use a small `useRouteId` helper that supports async route params while remaining compatible with the current React 18 test/runtime path.

## Commands Run

Backend:

```bash
python manage.py check
python manage.py makemigrations --check
python manage.py migrate
python -m pytest
python -m ruff check .
```

Frontend:

```bash
cd apps/frontend
npm audit
npm run lint
npm run typecheck
npm run test
npm run build
```

Docker:

```bash
docker compose config --quiet
docker compose -f docker-compose.yml -f docker-compose.prod.yml config --quiet
docker compose -f docker-compose.yml -f docker-compose.prod.yml build backend frontend
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
docker compose -f docker-compose.yml -f docker-compose.prod.yml exec -T backend python manage.py migrate
docker compose -f docker-compose.yml -f docker-compose.prod.yml exec -T backend python manage.py check
docker compose -f docker-compose.yml -f docker-compose.prod.yml ps
docker compose -f docker-compose.yml -f docker-compose.prod.yml logs backend --tail=80
docker compose -f docker-compose.yml -f docker-compose.prod.yml logs frontend --tail=80
docker compose -f docker-compose.yml -f docker-compose.prod.yml logs celery_worker --tail=80
docker compose -f docker-compose.yml -f docker-compose.prod.yml logs celery_beat --tail=80
docker compose -f docker-compose.yml -f docker-compose.prod.yml down
curl -I http://localhost:8000/admin/
```

## Backend Result

- `python manage.py check`: passed.
- `python manage.py makemigrations --check`: passed, no changes detected.
- `python manage.py migrate`: passed, no migrations to apply.
- `python -m pytest`: passed, 362 tests.
- `python -m ruff check .`: passed.

Observed warnings:

- DRF Decimal serializer warnings for `min_value` / `max_value` using non-Decimal values remain non-blocking and should be cleaned up in a later quality pass.
- Django 6.0 deprecation warning for repeated DRF format suffix converter registration appears during tests and should be monitored during future Django upgrades.

## Frontend Result

- `npm audit`: passed, 0 vulnerabilities.
- `npm run lint`: passed.
- `npm run typecheck`: passed.
- `npm run test`: passed, 51 files and 189 tests.
- `npm run build`: passed on Next.js 15.5.18.

Observed warning:

- `next lint` is deprecated and will be removed in Next.js 16. The project should migrate to the ESLint CLI before a future Next.js 16 upgrade.

## Docker Result

- `docker compose config --quiet`: passed.
- `docker compose -f docker-compose.yml -f docker-compose.prod.yml config --quiet`: passed.
- `docker compose -f docker-compose.yml -f docker-compose.prod.yml build backend frontend`: passed.
- `docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d`: passed with local smoke-test environment values.
- `docker compose -f docker-compose.yml -f docker-compose.prod.yml exec -T backend python manage.py migrate`: passed, no migrations to apply after initial smoke database setup.
- `docker compose -f docker-compose.yml -f docker-compose.prod.yml exec -T backend python manage.py check`: passed.
- `docker compose -f docker-compose.yml -f docker-compose.prod.yml ps`: all services running; PostgreSQL and Redis healthy.
- Backend health endpoint `http://localhost:8000/api/health/`: passed, HTTP 200.
- Deep health endpoint `http://localhost:8000/api/health/deep/`: passed, HTTP 200 with database and Redis checks true.
- Frontend `http://localhost:3000`: passed, HTTP 200.
- Login page `http://localhost:3000/login`: passed, HTTP 200.
- Admin route `http://localhost:8000/admin/`: responded with HTTP 302 to the admin login page.
- Backend, frontend, Celery worker, and Celery beat logs show successful startup.
- `docker compose -f docker-compose.yml -f docker-compose.prod.yml down`: completed after smoke testing.

Docker/config fixes made during the production smoke pass:

- `docker-compose.prod.yml` now uses `!override` for replacement production ports and media volumes instead of `!reset`, so localhost-only app ports and production media volumes are actually applied.
- Backend, Celery worker, and Celery beat now share the tagged `tcms-erp-backend:latest` image in the production Compose template.
- The production backend image now creates and runs as a non-root `tcms` system user. Celery worker and beat also run as this non-root user through the shared backend image.

## Documentation Result

- `docs/deployment/dependency-audit-report.md` confirms frontend npm vulnerabilities were remediated.
- `docs/deployment/frontend-dependency-upgrade-result.md` now reflects the final Next.js 15 route params compatibility fix.
- `docs/deployment/pre-release-verification-report.md` now links to this post-upgrade final verification.
- This report now includes the Step 23L production image build and smoke-test result.

## Remaining Known Issues

- Migrate `next lint` to ESLint CLI before Next.js 16.
- Optional cleanup: convert DRF Decimal serializer min/max values to `Decimal` instances to remove warnings.
- Optional cleanup: monitor DRF/Django converter deprecation before Django 6.

## Release Readiness Status

Release readiness is clean from application tests, type/lint checks, frontend audit, Docker Compose configuration, production image build, and local production-like smoke testing. Remaining items are deployment environment operations: real domains, real secrets, monitoring DSNs, backup targets, and staging/production infrastructure setup.
