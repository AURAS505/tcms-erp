# 0057 - Auth Rate Limiting

## Status
Accepted

## Context
Login and password reset endpoints are abuse-sensitive. TCMS ERP uses session-cookie authentication with CSRF protection, so the backend also needs rate limits for authentication and CSRF-token endpoints before production readiness.

## Decision
Auth-sensitive endpoints now use DRF `ScopedRateThrottle` with environment-configurable rates:

- `auth_login` for `POST /api/v1/auth/login/`
- `password_reset_request` for `POST /api/v1/auth/password-reset/request/`
- `password_reset_confirm` for `POST /api/v1/auth/password-reset/confirm/`
- `force_password_change` for `POST /api/v1/auth/force-password-change/`
- `csrf_token` for `GET /api/v1/auth/csrf/`

Local default rates are:

- `DJANGO_THROTTLE_AUTH_LOGIN=20/min`
- `DJANGO_THROTTLE_PASSWORD_RESET_REQUEST=5/min`
- `DJANGO_THROTTLE_PASSWORD_RESET_CONFIRM=10/min`
- `DJANGO_THROTTLE_FORCE_PASSWORD_CHANGE=10/min`
- `DJANGO_THROTTLE_CSRF_TOKEN=60/min`

Production examples use stricter rates and are documented in `.env.example` and `docs/deployment/production-security.md`.

## Security Behavior
Throttled requests return HTTP 429. Password reset request responses remain generic and do not reveal whether an email address exists.

## Future Improvements
If abuse patterns require stronger controls, add account lockout policy, CAPTCHA, IP reputation checks, or WAF rules. Those are intentionally not part of this step.
