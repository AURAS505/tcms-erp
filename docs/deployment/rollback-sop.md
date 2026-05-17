# Rollback SOP

Use this SOP when a production deployment introduces a severe regression that cannot be safely fixed forward within the approved incident window.

## When Rollback Is Required

Rollback should be considered when:

- Users cannot log in.
- Core dashboard or API health is down.
- Database migrations fail or corrupt expected behavior.
- Financial workflows produce incorrect results.
- Permission/branch isolation is compromised.
- Error rates remain high after restart/retry.
- Data loss or private file exposure is suspected.

## Immediate Actions

1. Declare incident status in the deployment channel.
2. Assign incident commander, rollback operator, and communications owner.
3. Stop non-essential changes.
4. Preserve logs and deployment timestamps.
5. Confirm the last known good revision and backup identifiers.

## Stop Current Deployment

Use the production platform's normal stop or scale-down process. For Docker Compose-style deployments:

```bash
docker compose stop backend frontend celery_worker celery_beat
```

Do not stop PostgreSQL or Redis unless the incident requires it.

## Restore Previous Image or Revision

Deploy the last known good image/revision:

```bash
git checkout <previous-release-tag>
docker compose build
docker compose up -d
```

Adapt commands to the production deployment platform. Confirm image tags before restarting services.

## Restore Database Backup for Migration or Data Issues

Only restore the database if rollback of application code is not enough or if migrations/data changes caused the issue.

Use the pre-deployment backup:

```bash
RESTORE_CONFIRM=yes scripts/restore_postgres.sh /var/backups/tcms-erp/postgres/tcms_erp_YYYYMMDDTHHMMSSZ.dump
```

Warnings:

- Database restore changes target data.
- Confirm production target before running.
- Record who approved restore and why.
- Preserve the failed-state backup first if forensic review is needed.

## Restore Media Backup If Needed

Use this only for media/private media corruption or accidental deletion:

```bash
RESTORE_CONFIRM=yes scripts/restore_media.sh /var/backups/tcms-erp/media/media_YYYYMMDDTHHMMSSZ.tar.gz
```

Confirm private media remains non-public after restore.

## Verify Rollback

- `GET /api/health/` succeeds.
- `GET /api/health/deep/` succeeds or returns known expected dependency status.
- Frontend loads.
- Login works.
- Protected dashboard loads.
- Student listing loads.
- Payment draft screen loads.
- Accounting trial balance report loads.
- Celery worker and beat are running if expected.
- Logs show no repeated critical errors.

Do not test fake financial postings in production during rollback verification.

## Communicate Rollback

Send a concise update:

- rollback status
- affected services
- expected user impact
- whether data restore occurred
- next update time
- support contact

Notify finance/admin owners if financial workflows were affected.

## Incident Notes Template

```text
Incident ID:
Date/time:
Release revision:
Rollback revision:
Incident commander:
Rollback operator:
Communications owner:

Issue summary:
User impact:
Detection source:

Actions taken:
- 

Database restored: yes/no
Database backup file:
Media restored: yes/no
Media backup file:

Verification results:
- Health:
- Login:
- Dashboard:
- Reports:
- Celery/Redis:

Root cause:
Follow-up actions:
Final status:
```

## After Rollback

- Keep incident notes with release records.
- Create follow-up issues for root cause and prevention.
- Do not retry production deployment until staging reproduces and validates the fix.
