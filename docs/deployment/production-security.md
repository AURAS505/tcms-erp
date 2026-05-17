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

- Login and password-reset rate limiting.
- Private file validation and storage hardening.
- Sentry or equivalent error monitoring.
- Backup automation and restore drills.
