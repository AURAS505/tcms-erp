# TCMS ERP

TCMS ERP is an enterprise-grade education management system for schools, colleges, coaching institutes, tuition centers, and multi-branch education businesses.

This repository contains the current TCMS ERP implementation, including backend APIs, frontend dashboard workflows, financial controls, deployment templates, and operational documentation.

## Current Scope

- Django REST Framework backend modules for accounts, organizations, academic years, students, guardians, teachers, classes, billing, payroll, accounting, reports, audit logs, and operational health.
- Next.js TypeScript dashboard with authenticated workflows for core academic, billing, payroll, accounting, reporting, and rollover views.
- Service-backed financial mutation APIs with branch scope, maker-checker controls, audit logging, immutability, and accounting posting protections.
- PostgreSQL, Redis, Celery worker, Celery beat, local Docker Compose, production Compose template, optimized production Dockerfiles, and deployment SOPs.
- Documentation for requirements, architecture, accounting principles, security, backup/restore, monitoring, go-live, rollback, and production deployment.

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
- Docker VPS deployment guide and production Compose template: `docs/deployment/docker-vps-deployment.md`, `docker-compose.prod.yml`
- Private file validation and storage guidance: `docs/deployment/file-storage-security.md`
- Monitoring, logging, health checks, and error tracking readiness: `docs/deployment/monitoring-and-logging.md`
- Backup automation and restore drills: `docs/deployment/backup-and-restore.md`
- Production release checklist: `docs/deployment/production-release-checklist.md`
- Go-live runbook: `docs/deployment/go-live-runbook.md`
- Rollback SOP: `docs/deployment/rollback-sop.md`
- Final UI polish plan: `docs/design/final-ui-polish-plan.md`

## Source Document Status

No existing project documents, SOP files, old code archives, or requirements files were found in the workspace before this scaffold was created. The master prompt has now been synced into repository documentation:

- `docs/requirements/master-requirements.md`
- `docs/requirements/nepali-date-academic-year.md`
- `docs/requirements/clarifications.md`
- `docs/accounting/financial-workflows.md`
- `docs/architecture/development-roadmap.md`

Add any additional signed SOPs or legacy documents under `docs/requirements/` before implementing business or financial logic.
