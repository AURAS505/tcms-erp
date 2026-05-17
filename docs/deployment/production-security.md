# Production Security Configuration

This guide covers the environment settings required to run TCMS ERP with browser session-cookie authentication, CSRF protection, explicit CORS origins, and HTTPS-aware cookie/header behavior.

## Required Backend Variables

Set these values in the backend deployment environment:

```env
DJANGO_ENV=production
DJANGO_DEBUG=false
DJANGO_SECRET_KEY=<long-random-secret>
DJANGO_ALLOWED_HOSTS=api.example.com
DJANGO_CORS_ALLOWED_ORIGINS=https://app.example.com
DJANGO_CORS_ALLOW_CREDENTIALS=true
DJANGO_CSRF_TRUSTED_ORIGINS=https://app.example.com
DATABASE_URL=postgres://user:password@postgres:5432/tcms_erp
REDIS_URL=redis://redis:6379/0
DJANGO_THROTTLE_AUTH_LOGIN=10/min
DJANGO_THROTTLE_PASSWORD_RESET_REQUEST=3/min
DJANGO_THROTTLE_PASSWORD_RESET_CONFIRM=5/min
DJANGO_THROTTLE_FORCE_PASSWORD_CHANGE=5/min
DJANGO_THROTTLE_CSRF_TOKEN=30/min
DJANGO_MEDIA_ROOT=/app/media
DJANGO_MEDIA_URL=/media/
DJANGO_PRIVATE_MEDIA_ROOT=/app/private_media
DJANGO_DEFAULT_FILE_STORAGE=django.core.files.storage.FileSystemStorage
DJANGO_MAX_UPLOAD_SIZE_BYTES=2097152
DJANGO_ALLOWED_UPLOAD_EXTENSIONS=pdf,jpg,jpeg,png,doc,docx
```

Do not use wildcard CORS origins when credentials are enabled. The backend raises a configuration error if credentials are combined with wildcard origins.

## Cookie and CSRF Settings

For HTTPS production deployments:

```env
DJANGO_SESSION_COOKIE_HTTPONLY=true
DJANGO_CSRF_COOKIE_HTTPONLY=false
DJANGO_SESSION_COOKIE_SECURE=true
DJANGO_CSRF_COOKIE_SECURE=true
DJANGO_SESSION_COOKIE_SAMESITE=Lax
DJANGO_CSRF_COOKIE_SAMESITE=Lax
```

The frontend obtains a CSRF token from `GET /api/v1/auth/csrf/` and sends it as `X-CSRFToken` for unsafe methods. CSRF is not disabled.

If the frontend and backend must run cross-site rather than same-site, review the browser cookie model carefully. Cross-site cookie flows generally require `SameSite=None` and secure HTTPS cookies.

## HTTPS and Reverse Proxy

When TLS terminates at a reverse proxy, set:

```env
DJANGO_SECURE_PROXY_SSL_HEADER=true
DJANGO_SECURE_SSL_REDIRECT=true
DJANGO_SECURE_HSTS_SECONDS=31536000
DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS=true
DJANGO_SECURE_HSTS_PRELOAD=true
```

Only enable HSTS preload once every subdomain is ready for HTTPS.

## Authentication Rate Limits

Auth-sensitive endpoints use DRF scoped throttling. Local defaults are intentionally usable for development:

```env
DJANGO_THROTTLE_AUTH_LOGIN=20/min
DJANGO_THROTTLE_PASSWORD_RESET_REQUEST=5/min
DJANGO_THROTTLE_PASSWORD_RESET_CONFIRM=10/min
DJANGO_THROTTLE_FORCE_PASSWORD_CHANGE=10/min
DJANGO_THROTTLE_CSRF_TOKEN=60/min
```

Recommended production starting values are:

```env
DJANGO_THROTTLE_AUTH_LOGIN=10/min
DJANGO_THROTTLE_PASSWORD_RESET_REQUEST=3/min
DJANGO_THROTTLE_PASSWORD_RESET_CONFIRM=5/min
DJANGO_THROTTLE_FORCE_PASSWORD_CHANGE=5/min
DJANGO_THROTTLE_CSRF_TOKEN=30/min
```

Password reset request responses remain generic and do not reveal whether an email exists. Throttled requests return HTTP 429.

## File Storage

Document references are currently metadata-only. Upload endpoints should use the common file validators before accepting files, keep sensitive files out of public media storage, and avoid trusting original filenames for storage paths.

See `docs/deployment/file-storage-security.md` for the private media design, upload size/extension settings, and S3-compatible storage guidance.

## Monitoring

Logging, health checks, frontend error boundaries, and optional Sentry-compatible environment placeholders are documented in `docs/deployment/monitoring-and-logging.md`.

## Backup and Restore

Database backup scripts, media/private media backup scripts, and restore drill SOPs are documented in `docs/deployment/backup-and-restore.md`.

## Release Operations

Production release checklist, go-live sequence, and rollback procedure are documented in:

- `docs/deployment/production-release-checklist.md`
- `docs/deployment/go-live-runbook.md`
- `docs/deployment/rollback-sop.md`

## Frontend Variable

Set the frontend API base URL to the deployed backend origin:

```env
NEXT_PUBLIC_API_BASE_URL=https://api.example.com
```

This must match the backend CORS and CSRF trusted origin configuration.

## Local Development

Local defaults remain intentionally relaxed:

```env
DJANGO_ENV=development
DJANGO_DEBUG=true
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,backend
DJANGO_CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
DJANGO_CSRF_TRUSTED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
DJANGO_SESSION_COOKIE_SECURE=false
DJANGO_CSRF_COOKIE_SECURE=false
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

## Configuration Guards

Production startup rejects:

- `DJANGO_DEBUG=true`
- missing or local placeholder `DJANGO_SECRET_KEY`
- missing `DJANGO_ALLOWED_HOSTS`
- missing CORS or CSRF trusted origins
- insecure session or CSRF cookies
- wildcard CORS origins with credentials

## Still Pending

- Authenticated private file download endpoints and signed URL support.
- MIME signature checks and optional malware scanning for uploaded files.
- Sentry or equivalent SDK wiring after the production monitoring provider is chosen.
- Deployment-specific backup scheduling and remote encrypted backup sync.
- Optional account lockout, CAPTCHA, or IP reputation controls if operational abuse requires stronger controls.
