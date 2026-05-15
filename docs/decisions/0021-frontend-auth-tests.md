# ADR 0021: Frontend Authentication Tests

## Status
Accepted

## Context
Step 19 added the frontend authentication foundation. The next hardening step is focused test coverage around API contract mapping, login redirects, dashboard guard states, and role-aware navigation without expanding the product UI.

## Decision
1. Add Vitest with jsdom and React Testing Library setup for frontend component tests.
2. Test `authService` request payloads and normalization of backend snake_case auth responses into frontend camelCase types.
3. Test login form required-field validation and success redirects to `/dashboard` or `/force-password-change`.
4. Test `AppShell` guard states: checking, unauthenticated, and authenticated.
5. Test `Sidebar` navigation rendering from the shared role config.
6. Keep Volt React Dashboard as reference-only for visual direction. No Volt source code, component names, template structure, Bootstrap dependency, or sample data is copied.

## Pending
Server-side auth middleware, broader role/permission navigation, React Query integration, and end-to-end auth flows remain pending. Student, teacher, class, billing, payroll, accounting, charts, and reports are still intentionally out of scope.

## Consequences
The auth foundation now has regression coverage for the highest-risk frontend contracts while preserving a small UI surface.

