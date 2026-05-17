# TCMS ERP

TCMS ERP is planned as an enterprise-grade education management system for schools, colleges, coaching institutes, tuition centers, and multi-branch education businesses.

This repository currently contains Step 1 only: monorepo foundation, Docker local development services, backend skeleton, frontend skeleton, environment sample, and initial documentation.

## Current Scope

- Monorepo structure under `tcms-erp/`
- Django REST Framework backend skeleton
- Next.js TypeScript frontend skeleton
- PostgreSQL, Redis, Celery worker, and Celery beat in Docker Compose
- Initial docs for architecture, API conventions, accounting principles, and local development

Business modules, database models, accounting posting logic, permissions, financial workflows, and production migrations are intentionally not implemented in Step 1.

## Repository Layout

```text
tcms-erp/
├── apps/
│   ├── backend/
│   └── frontend/
├── packages/
│   ├── shared-types/
│   └── config/
├── docs/
├── docker/
├── scripts/
├── docker-compose.yml
├── docker-compose.override.yml
├── .env.example
├── README.md
└── Makefile
```

## Local Development

```bash
cp .env.example .env
docker compose up --build
```

Services:

- Frontend: http://localhost:3000
- Backend health: http://localhost:8000/api/health/
- PostgreSQL: localhost:5432
- Redis: localhost:6379

## Production Security

Deployment documentation is indexed in `docs/deployment/README.md`.

- Production cookie, CSRF, CORS, HTTPS, and reverse proxy settings: `docs/deployment/production-security.md`
- Docker VPS deployment guide: `docs/deployment/docker-vps-deployment.md`
- Private file validation and storage guidance: `docs/deployment/file-storage-security.md`
- Monitoring, logging, health checks, and error tracking readiness: `docs/deployment/monitoring-and-logging.md`
- Backup automation and restore drills: `docs/deployment/backup-and-restore.md`
- Production release checklist: `docs/deployment/production-release-checklist.md`
- Go-live runbook: `docs/deployment/go-live-runbook.md`
- Rollback SOP: `docs/deployment/rollback-sop.md`

## Source Document Status

No existing project documents, SOP files, old code archives, or requirements files were found in the workspace before this scaffold was created. The master prompt has now been synced into repository documentation:

- `docs/requirements/master-requirements.md`
- `docs/requirements/nepali-date-academic-year.md`
- `docs/requirements/clarifications.md`
- `docs/accounting/financial-workflows.md`
- `docs/architecture/development-roadmap.md`

Add any additional signed SOPs or legacy documents under `docs/requirements/` before implementing business or financial logic.
