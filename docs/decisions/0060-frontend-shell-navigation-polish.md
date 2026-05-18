# 0060 - Frontend Shell Navigation Polish

## Status

Accepted

## Context

Step 24C implements Stage 2 of the final UI polish plan. The frontend already had a protected dashboard shell, sidebar, and topbar. The remaining issue was that the shell still felt like a basic scaffold: navigation was flat, mobile navigation was absent, and the topbar did not reflect the current route.

The Volt dashboard reference remains inspiration only. No Volt source code, Bootstrap dependency, or external template code was copied or imported.

## Decision

The AppShell, Sidebar, Topbar, and navigation config were polished while preserving the existing auth guard behavior and API contracts.

Changes:

- Added grouped navigation metadata for overview, people, academic, classes, billing, payroll, and accounting modules.
- Kept navigation config-driven so page links are not duplicated in layout components.
- Polished the dark sidebar treatment with stronger brand hierarchy, user context, grouped section labels, active route styling, and `aria-current`.
- Added a lightweight mobile navigation drawer controlled by AppShell and closed on navigation.
- Polished the topbar with route-derived page title, compact breadcrumb context, user role display, logout placement, and mobile menu trigger.
- Kept protected dashboard content hidden until authentication succeeds.

## Accessibility

- Sidebar exposes a primary navigation label.
- Active links use `aria-current="page"`.
- Mobile navigation opens as a dialog with a labeled close control.
- Topbar menu and logout controls remain keyboard-accessible buttons.

## Non-Goals

- No backend code was changed.
- No API contracts were changed.
- No business, billing, payroll, accounting, or security workflows were changed.
- No business pages, charts, or new large UI dependencies were added.

## Pending

Future polish can add finer-grained mobile transitions, iconography, and denser page-level layouts during the list/detail/form consistency pass.
