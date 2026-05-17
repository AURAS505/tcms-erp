# Monitoring and Logging

TCMS ERP is prepared for production observability with environment-driven logging, health checks, and optional error tracking configuration. Local development works without monitoring credentials.

During release and rollback operations, use this guide with `go-live-runbook.md` and `rollback-sop.md`.

## Backend Logging

Django logs to stdout/stderr through a console handler. Set the log level with:

```env
DJANGO_LOG_LEVEL=INFO
```

Use deployment log routing to send container logs to the selected platform. Do not log passwords, reset tokens, CSRF tokens, session IDs, authorization headers, or uploaded file contents.

## Error Tracking

Sentry-compatible placeholders are available:

```env
SENTRY_DSN=
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.05
NEXT_PUBLIC_SENTRY_DSN=
NEXT_PUBLIC_APP_ENV=production
```

No real DSN is committed. The current code does not require the Sentry SDK at runtime. Add the backend and frontend SDKs in a later step once the production monitoring provider is chosen.

## Health Checks

The lightweight health endpoint remains:

```text
GET /api/health/
```

The deeper dependency endpoint is:

```text
GET /api/health/deep/
```

Deep health checks the database by default. Redis checking is optional and controlled by:

```env
DJANGO_DEEP_HEALTH_CHECK_REDIS=true
```

The deep endpoint returns no secrets or connection strings.

## Frontend Error Handling

The frontend includes a global Next.js error boundary at `apps/frontend/app/error.tsx`. It shows a clean user-facing error state and does not expose stack traces in the UI. Development mode logs the error to the browser console for debugging.

## Pending Work

- Add backend and frontend Sentry SDK initialization after choosing the production project and DSNs.
- Add release/version tagging for backend and frontend deployments.
- Add uptime monitoring against `/api/health/` and `/api/health/deep/`.
- Add centralized log retention and alerting rules.
- Add business metrics and audit dashboards after production workflows stabilize.
