# Backup and Restore SOP

Backups are not operationally real until a restore has been tested. TCMS ERP production operations must include database backups, private media backups, retention monitoring, and scheduled restore drills.

## Environment Variables

Set these values in the environment that runs the scripts:

```env
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=tcms_erp
POSTGRES_USER=tcms
POSTGRES_PASSWORD=<secret>
BACKUP_DIR=/var/backups/tcms-erp
BACKUP_RETENTION_DAYS=30
DJANGO_MEDIA_ROOT=/app/media
DJANGO_PRIVATE_MEDIA_ROOT=/app/private_media
BACKUP_REMOTE_TARGET=
BACKUP_ENCRYPTION_ENABLED=true
```

Do not commit real credentials. The scripts pass `POSTGRES_PASSWORD` through `PGPASSWORD` and do not print it.

## Daily Database Backup SOP

Run:

```bash
scripts/backup_postgres.sh
```

The script creates a timestamped PostgreSQL custom-format dump under:

```text
${BACKUP_DIR}/postgres/
```

Recommended production schedule:

- Run daily during the lowest traffic period.
- Keep at least 30 days of local backups.
- Copy backups to remote encrypted storage after local creation.
- Alert when a backup job fails or no new backup exists within 24 hours.

## Media and Private Media Backup SOP

Run:

```bash
scripts/backup_media.sh
```

The script packages `DJANGO_MEDIA_ROOT` and `DJANGO_PRIVATE_MEDIA_ROOT` into a timestamped tarball under:

```text
${BACKUP_DIR}/media/
```

Sensitive documents should remain private. Do not expose private media directories through a public web server.

For future S3-compatible storage, use provider-specific private bucket replication or sync tooling. Keep buckets private, encrypted, and protected from public ACLs.

## Restore Database Procedure

Use a staging environment first.

```bash
RESTORE_CONFIRM=yes scripts/restore_postgres.sh /var/backups/tcms-erp/postgres/tcms_erp_YYYYMMDDTHHMMSSZ.dump
```

Without `RESTORE_CONFIRM=yes`, the script prompts for `RESTORE`.

Restore warnings:

- Confirm the target database before running.
- Restoring can overwrite or change target data.
- Never test restore directly against production unless executing a declared disaster recovery operation.

## Restore Media Procedure

Use:

```bash
RESTORE_CONFIRM=yes scripts/restore_media.sh /var/backups/tcms-erp/media/media_YYYYMMDDTHHMMSSZ.tar.gz
```

The restore script copies archived `media/` and `private_media/` contents into the configured media roots.

## Quarterly Restore Drill Checklist

1. Provision an isolated staging environment.
2. Restore the latest PostgreSQL backup.
3. Restore the latest media/private media backup.
4. Run database migrations to confirm compatibility.
5. Start backend and frontend services.
6. Verify login, dashboard load, reports, and a representative read-only document reference.
7. Confirm no production email/SMS/payment integrations are active in the drill environment.
8. Record restore duration, backup timestamp, operator, issues, and corrective actions.

## Backup Verification Checklist

- Backup file exists and is non-empty.
- Backup timestamp is within the expected schedule.
- Backup directory permissions are restricted.
- Remote copy completed where configured.
- Retention cleanup did not delete the newest backup.
- Restore drill has passed within the last quarter.

## Disaster Recovery Notes

Keep database and media backups from the same operational window when possible. Accounting, billing, payroll, and audit logs live in PostgreSQL, while uploaded/supporting documents live in media/private media storage. Both are required for a complete recovery.

## Pending Work

- Add deployment-specific cron/systemd/Kubernetes job configuration.
- Add encrypted remote backup sync implementation.
- Add backup job monitoring and alerts.
- Add documented recovery time and recovery point objectives after production infrastructure is finalized.
