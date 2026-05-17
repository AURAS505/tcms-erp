# Production Release Checklist

Use this checklist before every TCMS ERP production release. Do not proceed unless the release owner, technical owner, and business sign-off owner have approved the deployment window.

## Pre-Release Checklist

- Release branch/tag is identified.
- Changelog or release notes are prepared.
- Deployment window is approved.
- Change freeze is announced to staff.
- Rollback owner is assigned.
- Backup and restore owner is assigned.
- Staging validation has completed on the same revision.

## Environment Variable Checklist

- `DJANGO_ENV=production`
- `DJANGO_DEBUG=false`
- `DJANGO_SECRET_KEY` is strong and not shared in source control.
- `DJANGO_ALLOWED_HOSTS` is explicit.
- `DJANGO_CORS_ALLOWED_ORIGINS` is explicit.
- `DJANGO_CORS_ALLOW_CREDENTIALS=true` without wildcard origins.
- `DJANGO_CSRF_TRUSTED_ORIGINS` is explicit.
- `DATABASE_URL`, `REDIS_URL`, and Celery broker/result URLs are production values.
- Cookie security flags match `production-security.md`.
- Backup variables match `backup-and-restore.md`.
- Monitoring/logging variables match `monitoring-and-logging.md`.

## Security Checklist

- HTTPS is active at the public entrypoint.
- Reverse proxy forwards `X-Forwarded-Proto` correctly if used.
- Secure session and CSRF cookies are enabled.
- HSTS settings are reviewed before enabling preload.
- Auth rate limits are configured.
- No real secrets are committed to the repository.
- Admin access is restricted to authorized staff.

## Database Migration Checklist

- `python manage.py makemigrations --check` passes.
- `python manage.py migrate --plan` is reviewed for production impact.
- Migrations have been applied successfully in staging.
- Backward-incompatible migrations are documented.
- Rollback impact of migrations is understood.

## Backup Checklist

- Run `scripts/backup_postgres.sh` immediately before deployment.
- Run `scripts/backup_media.sh` immediately before deployment.
- Confirm backup files exist and are non-empty.
- Confirm backup timestamp is current.
- Confirm remote/encrypted copy completed if configured.
- Confirm a restore drill has passed before first production go-live.

## Frontend Build Checklist

- `npm run lint` passes.
- `npm run typecheck` passes.
- `npm run test` passes.
- `npm run build` passes.
- `NEXT_PUBLIC_API_BASE_URL` points to the production backend origin.

## Backend Test Checklist

- `python manage.py check` passes.
- `python -m pytest` passes.
- `python -m ruff check .` passes.
- Health endpoints are available in staging.

## Celery and Redis Checklist

- Redis is reachable.
- Celery worker starts without import/config errors.
- Celery beat starts if scheduled jobs are enabled.
- Worker logs are visible in monitoring.

## Static and Media Checklist

- Static assets are collected or served by the deployment platform.
- `DJANGO_MEDIA_ROOT` and `DJANGO_PRIVATE_MEDIA_ROOT` are configured.
- Private media is not exposed publicly.
- File upload limits and extension allow-list are configured.

## Smoke Test Checklist

- `GET /api/health/` returns healthy.
- `GET /api/health/deep/` returns healthy or known expected dependency status.
- Frontend loads.
- Login works.
- Protected dashboard loads.
- Student list loads.
- Payment draft screen loads.
- Accounting trial balance report loads.
- Audit log list is read-only.

## Financial Controls Checklist

- Trial balance report loads in staging.
- Payment posting is not tested on production with fake financial data unless using a dedicated test tenant/database.
- Financial mutation endpoints are restricted to Super Admin, Institute Owner, Accountant, or intended role.
- Auditor remains read-only.
- Posted financial records remain immutable.
- Audit logs are checked after a staging test mutation.
- Backup and restore verification is complete before real go-live.

## Sign-Off Checklist

- Technical lead approves.
- Finance/accounting owner approves.
- Operations owner approves.
- Support handover owner approves.
- Rollback owner confirms rollback readiness.
- Go-live start time is recorded.
