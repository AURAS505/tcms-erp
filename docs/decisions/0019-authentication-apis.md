# ADR 0019: Authentication APIs

## Status
Accepted

## Context
The backend API foundation requires a secure authentication layer before the Next.js frontend can implement login, protected routing, and role-aware navigation. TCMS ERP also needs password reset, forced password change, session tracking, and branch/role context for backend-enforced permissions.

## Decision
1. Add authentication endpoints under `/api/v1/auth/`.
2. Use Django session authentication so the web frontend can use secure cookie-compatible flows.
3. Support login with either email or username.
4. Return a safe current-user payload containing roles, permissions, branch assignments, and `force_password_change`.
5. Store password reset tokens as SHA-256 hashes only.
6. Keep password reset request responses generic so email existence is not disclosed.
7. Return a raw reset token only when `DEBUG=True`, for local development and automated tests.
8. Add forced password change support for first-login or admin-reset flows.
9. Track login sessions in `LoginSession` where a Django session key is available.
10. Keep all non-auth `/api/v1/` endpoints authenticated by default.

## Routes
- `POST /api/v1/auth/login/`
- `POST /api/v1/auth/logout/`
- `GET /api/v1/auth/me/`
- `GET /api/v1/auth/session/`
- `POST /api/v1/auth/password-reset/request/`
- `POST /api/v1/auth/password-reset/confirm/`
- `POST /api/v1/auth/force-password-change/`

## Security Notes
Password reset tokens are never stored raw. Production email delivery is intentionally left as a later integration; this step creates the token safely and documents the local-development debug behavior. Rate limiting is still pending and should be added before public production deployment.

## Not Implemented
- Frontend login pages.
- OAuth or social login.
- Two-factor authentication.
- Production email templates and delivery.
- Dedicated rate limiting middleware.
- Billing, payroll, accounting posting, or rollover mutation APIs.
