# Go-Live Runbook

This runbook describes the operational sequence for a TCMS ERP production go-live. Execute it during an approved deployment window only.

## 1. Deployment Window Preparation

- Confirm release commit/tag.
- Confirm deployment owner, backup owner, rollback owner, and communications owner.
- Confirm all sign-offs in `production-release-checklist.md`.
- Confirm support staff availability during and after deployment.
- Open a shared incident/deployment log for timestamps and notes.

## 2. Freeze and Change Control

- Announce change freeze to staff.
- Stop manual operational changes that could conflict with deployment.
- Confirm no finance close, payroll posting, or rollover operation is in progress.
- Confirm no backup or restore job is running.

## 3. Backup Immediately Before Deployment

Run database backup:

```bash
scripts/backup_postgres.sh
```

Run media/private media backup:

```bash
scripts/backup_media.sh
```

Record:

- backup filenames
- backup timestamp
- operator
- remote copy status if configured

Do not proceed if the backup is missing, empty, or failed.

## 4. Pull and Build Deployment Images

- Pull the approved revision.
- Build backend image.
- Build frontend image.
- Build or refresh Celery worker/beat image if separated.
- Confirm image tags map to the approved release.

Example for Docker Compose-style deployments:

```bash
docker compose pull
docker compose build
```

Adapt commands to the production platform.

## 5. Apply Migrations

Review plan:

```bash
python manage.py migrate --plan
```

Apply migrations:

```bash
python manage.py migrate
```

Stop and escalate if migrations fail.

## 6. Start or Restart Services

- Start/restart backend web service.
- Start/restart frontend service.
- Start/restart Celery worker.
- Start/restart Celery beat if used.
- Confirm Redis and PostgreSQL are healthy.

Example:

```bash
docker compose up -d
```

## 7. Verify Health Endpoints

Check:

```text
GET /api/health/
GET /api/health/deep/
```

Expected:

- `/api/health/` returns success.
- `/api/health/deep/` shows database healthy and Redis healthy if Redis deep check is enabled.

## 8. Frontend and Access Smoke Tests

- Frontend home/login page loads.
- Login works with a production-approved test account.
- Protected dashboard access works.
- Logout works.
- Unauthorized/private routes remain protected.

## 9. Business Smoke Tests

Use read-only checks on production unless using a dedicated test tenant/database:

- Student listing loads.
- Payment draft screen loads.
- Payroll payment draft screen loads.
- Accounting trial balance report loads.
- General ledger report loads.
- Academic year list loads.

Do not post fake payments, payroll, journals, or rollovers in production.

## 10. Celery and Redis Verification

- Celery worker process is running.
- Celery beat process is running if scheduled jobs are enabled.
- Worker logs are visible.
- Redis health is stable.
- No repeated task import/config errors appear.

## 11. Logs and Monitoring Verification

- Backend logs are streaming.
- Frontend error boundary does not show for normal navigation.
- `/api/health/` uptime monitor is green if configured.
- Error tracking DSN is active only if production monitoring provider has been configured.
- No repeated 500 errors appear during smoke tests.

## 12. Staff Handover Checklist

- Confirm go-live status to operations staff.
- Share known limitations.
- Share support escalation path.
- Confirm finance staff understand production mutation rules.
- Confirm support staff know rollback owner and incident channel.
- Record deployment completion time.

## 13. Post-Go-Live Monitoring Window

Monitor for at least the agreed window after deployment:

- API error rates
- Login and CSRF failures
- Database connectivity
- Redis/Celery health
- Slow requests
- Failed financial mutation attempts
- Unexpected permission errors

If severe issues appear, follow `rollback-sop.md`.
