# ADR 0023: Frontend Route Protection Middleware

## Status
Accepted

## Context
The dashboard already has a client-side `AppShell` guard backed by the shared auth provider. Direct dashboard URL requests still rendered the page shell before the client auth check completed. A lightweight server-side middleware check reduces that flash for clearly unauthenticated users.

## Decision
1. Add Next.js middleware for `/dashboard` and `/dashboard/*`.
2. Redirect requests without a likely session cookie to `/login`.
3. Preserve the requested dashboard path in a `redirect` query parameter.
4. Use Django's common `sessionid` cookie name as the current session-cookie assumption.
5. Keep public auth pages, static assets, and Next.js internals outside the middleware matcher.
6. Keep `AppShell` client verification active through `/api/v1/auth/me/`; middleware is only a first-pass route gate.
7. Keep Volt React Dashboard reference-only. No Volt source code, component names, sample data, Bootstrap dependency, or template structure is copied.

## Login Redirect
After successful login, the login page redirects to the sanitized `redirect` value when it points to `/dashboard` or a dashboard child route. If the user must change their password, `/force-password-change` still takes priority.

## Pending Hardening
Production deployments may customize Django's session cookie name, domain, SameSite, Secure, or proxy behavior. Middleware configuration should be revisited with the final production session settings. Backend authorization remains authoritative.

