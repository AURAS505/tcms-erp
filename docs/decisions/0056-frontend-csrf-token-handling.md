# 0056 - Frontend CSRF Token Handling

## Status
Accepted

## Context
The backend uses Django session-cookie authentication with CSRF middleware enabled. Step 22A added `GET /api/v1/auth/csrf/` so browser clients can safely obtain a CSRF cookie and token before making authenticated mutation requests.

## Decision
The shared frontend API client now handles CSRF centrally:

- Safe requests such as `GET` do not fetch or send a CSRF token.
- Unsafe requests (`POST`, `PUT`, `PATCH`, `DELETE`) fetch `GET /api/v1/auth/csrf/` before the first mutation when no token is cached.
- The token is read from the backend response and falls back to the `csrftoken` cookie when available.
- Mutation requests include `X-CSRFToken`.
- All API calls continue to use `credentials: include`.

This keeps billing, payroll, accounting, academic rollover, and auth mutations compatible with Django's session-cookie CSRF protection without duplicating logic in each module.

## Security Notes
CSRF protection remains enabled. The frontend does not disable or bypass Django CSRF checks, and failed CSRF token fetches surface as API errors rather than silently retrying.

## Remaining Production Work
Production deployment should configure cookie security settings for the final domains, including trusted origins, secure cookies, and same-site policy appropriate for the deployed frontend/backend topology.
