# Docker VPS Deployment Guide

This guide documents the recommended default production target for TCMS ERP when no managed platform has been selected: an Ubuntu VPS running Docker Compose behind Nginx with HTTPS.

If the deployment target later changes to Render, Railway, AWS, DigitalOcean App Platform, Kubernetes, or another managed PaaS, create a new platform-specific guide instead of reusing VPS assumptions.

## Recommended Server Requirements

Starting point for a small production tenant:

- Ubuntu 22.04 LTS or 24.04 LTS
- 2 vCPU minimum
- 4 GB RAM minimum
- 40 GB SSD minimum
- Daily snapshot or block-volume backup support
- Firewall allowing only SSH, HTTP, and HTTPS publicly

Increase CPU, RAM, and disk when student count, uploaded documents, reports, or Celery workload grows.

## Required Software

Install:

- Docker Engine
- Docker Compose plugin
- Git
- Nginx or equivalent reverse proxy
- Certbot for Let's Encrypt, or SSL from the reverse proxy provider

Keep OS packages patched and restrict SSH access to authorized operators.

## Server Directory Layout

Suggested layout:

```text
/srv/tcms-erp/
├── repo/
├── env/
│   └── production.env
├── backups/
├── media/
└── private_media/
```

Do not store real secrets in Git. Keep `production.env` readable only by deployment operators.

## Clone Repository

```bash
sudo mkdir -p /srv/tcms-erp
sudo chown "$USER":"$USER" /srv/tcms-erp
cd /srv/tcms-erp
git clone <repository-url> repo
cd repo
```

Checkout the approved release tag or commit from `production-release-checklist.md`.

## Create Production Environment File

Start from `.env.example`, copy it outside the repository, and replace placeholder values:

```bash
cp .env.example /srv/tcms-erp/env/production.env
chmod 600 /srv/tcms-erp/env/production.env
```

Required backend values include:

```env
DJANGO_ENV=production
DJANGO_DEBUG=false
DJANGO_SECRET_KEY=<long-random-secret>
DJANGO_ALLOWED_HOSTS=api.example.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://app.example.com
DJANGO_CORS_ALLOWED_ORIGINS=https://app.example.com
DJANGO_CORS_ALLOW_CREDENTIALS=true
DJANGO_SESSION_COOKIE_SECURE=true
DJANGO_CSRF_COOKIE_SECURE=true
DJANGO_SECURE_SSL_REDIRECT=true
DJANGO_SECURE_PROXY_SSL_HEADER=true
DATABASE_URL=postgres://tcms:<password>@postgres:5432/tcms_erp
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1
DJANGO_MEDIA_ROOT=/app/media
DJANGO_PRIVATE_MEDIA_ROOT=/app/private_media
BACKUP_DIR=/srv/tcms-erp/backups
```

Required frontend values:

```env
NEXT_PUBLIC_API_BASE_URL=https://api.example.com
NEXT_PUBLIC_APP_ENV=production
NEXT_PUBLIC_SENTRY_DSN=
```

Use real domain names only in the private production environment file.

## Database and Redis Setup

The current `docker-compose.yml` includes PostgreSQL and Redis services. For a single-VPS deployment this is acceptable as a starting point if:

- PostgreSQL data is stored on a persistent Docker volume.
- Redis data is stored on a persistent Docker volume.
- Backups are scheduled and restore-tested.
- Database ports are not exposed publicly by firewall rules.

For larger deployments, move PostgreSQL to a managed database or dedicated database host and update `DATABASE_URL`.

## Production Compose Notes

The repository Compose file is optimized for local development:

- backend uses `python manage.py runserver`
- frontend uses `npm run dev`
- source directories are bind-mounted
- `.env.example` is referenced directly

For production, create a deployment-specific Compose override or production Compose file that:

- uses `/srv/tcms-erp/env/production.env`
- runs backend through Gunicorn
- runs frontend through `next start` after build
- mounts persistent `media` and `private_media` directories
- avoids exposing PostgreSQL and Redis publicly
- uses Docker restart policies such as `restart: unless-stopped`

This repository includes a production-oriented template at `docker-compose.prod.yml`. It resets development bind mounts, uses Gunicorn for Django, uses `next start` for the frontend after building, mounts persistent media volumes, removes public PostgreSQL/Redis ports, and binds backend/frontend ports to localhost for Nginx.

Example backend command:

```yaml
command: gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

Example frontend command:

```yaml
command: npm run start
```

## Build Containers

From the approved release:

```bash
docker compose --env-file /srv/tcms-erp/env/production.env build
```

If using a production override:

```bash
TCMS_ENV_FILE=/srv/tcms-erp/env/production.env \
  docker compose --env-file /srv/tcms-erp/env/production.env -f docker-compose.yml -f docker-compose.prod.yml build
```

## Run Migrations

Review first:

```bash
TCMS_ENV_FILE=/srv/tcms-erp/env/production.env \
  docker compose --env-file /srv/tcms-erp/env/production.env -f docker-compose.yml -f docker-compose.prod.yml run --rm backend python manage.py migrate --plan
```

Apply:

```bash
TCMS_ENV_FILE=/srv/tcms-erp/env/production.env \
  docker compose --env-file /srv/tcms-erp/env/production.env -f docker-compose.yml -f docker-compose.prod.yml run --rm backend python manage.py migrate
```

Run backups immediately before applying production migrations.

## Create Superuser

Create only approved admin accounts:

```bash
TCMS_ENV_FILE=/srv/tcms-erp/env/production.env \
  docker compose --env-file /srv/tcms-erp/env/production.env -f docker-compose.yml -f docker-compose.prod.yml run --rm backend python manage.py createsuperuser
```

Use strong credentials and remove temporary accounts after go-live.

## Start Services

```bash
TCMS_ENV_FILE=/srv/tcms-erp/env/production.env \
  docker compose --env-file /srv/tcms-erp/env/production.env -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

Check:

```bash
docker compose ps
docker compose logs --tail=100 backend
docker compose logs --tail=100 celery_worker
docker compose logs --tail=100 celery_beat
```

## Static, Media, and Private Media

Use persistent directories:

```text
/srv/tcms-erp/media
/srv/tcms-erp/private_media
```

Do not expose private media through Nginx. Use `file-storage-security.md` for private document guidance. Set Nginx upload limit to match or exceed `DJANGO_MAX_UPLOAD_SIZE_BYTES`.

Static files are currently served by the frontend build and Django admin/static needs should be reviewed for the final production reverse proxy. If backend static serving is required, add an explicit static collection/serving strategy before go-live.

## SSL and HTTPS

Use Certbot or provider-managed SSL. Production settings should have secure cookies and HTTPS redirect enabled. If TLS terminates at Nginx, set:

```env
DJANGO_SECURE_PROXY_SSL_HEADER=true
```

## Nginx Reverse Proxy Example

Placeholder example only. Replace domains with real production domains in server config, not in Git.

```nginx
server {
    listen 80;
    server_name app.example.com api.example.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.example.com;

    ssl_certificate /etc/letsencrypt/live/api.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.example.com/privkey.pem;

    client_max_body_size 2m;

    add_header X-Content-Type-Options nosniff always;
    add_header X-Frame-Options DENY always;
    add_header Referrer-Policy same-origin always;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
    }
}

server {
    listen 443 ssl http2;
    server_name app.example.com;

    ssl_certificate /etc/letsencrypt/live/app.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/app.example.com/privkey.pem;

    add_header X-Content-Type-Options nosniff always;
    add_header X-Frame-Options DENY always;
    add_header Referrer-Policy same-origin always;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
    }
}
```

If WebSockets are added later, extend the proxy config with upgrade headers for the relevant location.

## Celery Worker and Beat Checks

Verify:

```bash
docker compose ps celery_worker celery_beat redis
docker compose logs --tail=100 celery_worker
docker compose logs --tail=100 celery_beat
```

Celery worker and beat should run without import errors or repeated Redis connection failures.

## Health Checks

Check:

```text
https://api.example.com/api/health/
https://api.example.com/api/health/deep/
```

Deep health should show database healthy. Redis is included only if `DJANGO_DEEP_HEALTH_CHECK_REDIS=true`.

## Backup Scheduling

Use `backup-and-restore.md` and schedule:

- daily `scripts/backup_postgres.sh`
- daily `scripts/backup_media.sh`
- remote encrypted copy after local backup
- quarterly restore drill

Do not consider backups complete until a restore drill passes.

## Monitoring and Logging

Use `monitoring-and-logging.md`:

- route Docker logs to the selected log platform
- monitor `/api/health/`
- monitor `/api/health/deep/`
- configure Sentry or equivalent after provider selection

## Deployment Update Process

For every update:

1. Complete `production-release-checklist.md`.
2. Announce deployment window and freeze.
3. Run fresh database and media backups.
4. Pull the approved revision.
5. Build images.
6. Review and apply migrations.
7. Restart services.
8. Run smoke tests from `go-live-runbook.md`.
9. Monitor post-deployment logs and health checks.

## Rollback Reference

Use `rollback-sop.md` if deployment causes severe login, health, permission, financial, data, or availability issues.

Database restore is a separate decision from application rollback. Use it only when migration/data changes require it.

## Start on Reboot

Preferred options:

- Docker restart policies in the production Compose file, such as `restart: unless-stopped`.
- A small systemd unit that runs `docker compose up -d` from the deployment directory.

Document the chosen option in the server operations notes.
