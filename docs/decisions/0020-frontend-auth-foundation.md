# ADR 0020: Frontend Authentication Foundation

## Status
Accepted

## Context
The backend authentication APIs are available under `/api/v1/auth/`. The frontend needs a small Next.js foundation for login, password reset, forced password change, session checks, and a protected dashboard shell before operational modules are added.

## Decision
1. Keep the existing Next.js App Router, TypeScript, and Tailwind stack.
2. Add a compact API client that uses `NEXT_PUBLIC_API_BASE_URL` with `http://localhost:8000` as the local default.
3. Add auth service functions for login, logout, current user, session check, password reset request, password reset confirm, and forced password change.
4. Normalize backend snake_case auth payloads into frontend camelCase types.
5. Use Volt React Dashboard only as a visual reference for a clean admin style: dark sidebar, white topbar, light background, compact cards, and simple form controls.
6. Do not copy Volt source code, import its repository, add Bootstrap, or recreate the template.
7. Use a client-side route guard placeholder in `AppShell` that calls `/api/v1/auth/me/` and shows a sign-in prompt when unauthenticated.
8. Keep navigation role-aware through one shared config array. Backend authorization remains authoritative.

## Auth Flow
- `/login` posts credentials to `/api/v1/auth/login/`.
- Successful login redirects users with `force_password_change=true` to `/force-password-change`; all others go to `/dashboard`.
- `/dashboard` is wrapped in the protected dashboard shell and loads the current user from `/api/v1/auth/me/`.
- Logout posts to `/api/v1/auth/logout/` and returns to `/login`.
- `/forgot-password` posts to `/api/v1/auth/password-reset/request/`.
- `/reset-password` posts token and new password to `/api/v1/auth/password-reset/confirm/`.
- `/force-password-change` posts current and new passwords to `/api/v1/auth/force-password-change/`.

## Pending Frontend Modules
Student, guardian, teacher, class, billing, payroll, accounting, reporting, settings, charts, and operational workflow pages are intentionally not implemented in this foundation step.

## Testing
Frontend test tooling exists through Vitest and React Testing Library. No component tests are added in this step because the screens are thin integration placeholders around backend auth APIs; focused tests should be added when shared form behavior and data hooks stabilize.

## Consequences
The frontend now has reusable auth, form, shell, sidebar, topbar, and navigation primitives. The dashboard content remains minimal until module APIs and permissions are expanded.
