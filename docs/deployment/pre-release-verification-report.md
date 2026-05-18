# Pre-Release Verification Report

Date: 2026-05-17

## Summary

Final pre-release verification was completed for backend, frontend, Docker configuration, production templates, deployment documentation, and SOP/security alignment. Clear documentation drift was fixed in `README.md`; it no longer describes the repository as a Step 1 skeleton.

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
```

Scripts:

```bash
bash -n scripts/backup_postgres.sh
bash -n scripts/restore_postgres.sh
bash -n scripts/backup_media.sh
bash -n scripts/restore_media.sh
```

## Results

- `python manage.py check`: passed.
- `python manage.py makemigrations --check`: passed, no changes detected.
- `python manage.py migrate`: passed.
- `python -m pytest`: passed, 362 tests.
- `python -m ruff check .`: passed.
- `npm run lint`: passed.
- `npm run typecheck`: passed.
- `npm run test`: passed, 189 tests.
- `npm run build`: passed.
- `docker compose config --quiet`: passed.
- `docker compose -f docker-compose.yml -f docker-compose.prod.yml config --quiet`: passed.
- `docker compose -f docker-compose.yml -f docker-compose.prod.yml build backend frontend`: passed.
- `bash -n` script checks: not available in this Windows environment because the Bash shim routes to WSL and WSL does not have `/bin/bash` installed.

## Fixes Made

- Updated `README.md` to remove stale Step 1-only language.
- Added this pre-release verification report.

No backend, frontend, accounting, permission, or financial workflow logic was changed.

## Documentation Review

- Deployment documentation is indexed in `docs/deployment/README.md`.
- Production security docs are linked from `README.md`.
- Backup/restore docs and scripts are linked.
- Monitoring/logging docs are linked.
- Docker VPS deployment docs reference `docker-compose.prod.yml`, production Dockerfiles, env-file usage, migration commands, and frontend build-time public env behavior.
- Local reference/sample directories are ignored by Git and Docker build contexts.

## SOP and Security Spot Check

- Backend financial mutation APIs are service-backed and covered by permission, branch-scope, immutability, maker-checker, and posting tests.
- Branch-scoped financial mutation tests exist for billing and payroll.
- Accounting journal mutation/reversal tests cover posting, reversal, immutability, and closed-period protections.
- Academic rollover tests cover validation, execution, hard close, and hard-closed posting protection.
- Frontend API client fetches and sends CSRF tokens for unsafe methods.
- Auth-sensitive endpoint rate limiting is configured and tested.
- Audit logging exists for sensitive financial workflows and is covered by service/API tests.
- Docker production template keeps PostgreSQL and Redis ports non-public and binds app ports to localhost for reverse proxying.

## Known Limitations

- Shell script syntax checks need a Unix-like shell or a working WSL/Git Bash installation.
- Frontend dependency audit during Docker build reports npm vulnerabilities in the current dependency tree; see `docs/deployment/dependency-audit-report.md` for the focused audit and remediation decision.
- Production deployment still needs platform-specific real domains, secrets, remote backup sync, monitoring provider DSNs, and formal RTO/RPO values.
- Backend static/admin asset serving strategy should be finalized before go-live if Django admin/static files are required in production.

## Production Readiness Status

The repository is pre-release ready from the available local verification perspective. All application tests, lint/type checks, local and production Docker Compose validation, and production Docker image builds passed. Remaining items are environment/platform operations rather than application workflow blockers.

## Remaining Future Enhancements

- Plan a dedicated major-version dependency upgrade for the unresolved Next.js and Vitest audit findings.
- Wire a real monitoring provider SDK and release tagging.
- Add encrypted remote backup sync and scheduled job examples.
- Finalize production static/admin asset serving.
- Define formal RTO/RPO targets with the operating team.
