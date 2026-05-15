# ADR 0022: Frontend Auth Provider

## Status
Accepted

## Context
The frontend authentication foundation had working auth service functions and route guard tests, but protected surfaces would call `/api/v1/auth/me/` independently as new pages were added. A shared provider is needed before operational modules so user, role, permission, and branch assignment state can be reused.

## Decision
1. Add a root `AppProviders` client component with a single React Query `QueryClientProvider`.
2. Add `AuthProvider` that loads the current user through `authService.currentUser` and stores the result in React Query session state.
3. Expose a compact `useAuth` hook with user, loading, error, login, logout, refreshSession, `hasRole`, `hasPermission`, permissions, and branch assignments.
4. Refactor `AppShell` to use shared auth state instead of calling `/me/` directly.
5. Refactor login to use the provider login helper so successful login updates the shared session cache.
6. Keep Volt React Dashboard reference-only. No Volt source code, component names, sample data, Bootstrap dependency, or template structure is copied.

## Pending Limitations
Server-side auth middleware, React Query persistence, token refresh, broader navigation, and end-to-end auth browser flows are still pending. Student, teacher, class, billing, payroll, accounting, charts, reports, and settings pages remain out of scope.

## Consequences
Authenticated frontend pages can now share one cached user/session source and avoid repeated `/me/` calls as the dashboard grows.

