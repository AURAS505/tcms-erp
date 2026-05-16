# ADR 0031: Frontend Report Filters

## Status
Accepted

## Context
Accounting report pages were read-only and URL-driven, but users needed to know and manually enter query parameters such as `organization`. The backend already exposes organization, branch, academic year, and academic period endpoints that can provide lightweight lookup data for report filtering.

## Decision
1. Add lookup types and API helpers for organizations, branches, academic years, and academic periods.
2. Add a reusable `ReportFilters` component for accounting reports.
3. Preserve selected report filters in URL search parameters.
4. Keep report loading disabled until an organization is selected.
5. Keep report pages read-only and reuse existing report API helpers.
6. Keep Volt React Dashboard reference-only for general admin spacing, cards, and form feel. No Volt source code, component names, sample data, Bootstrap dependency, or template structure is copied.

## Pending
Report exports, PDF output, charts, saved report presets, account selector filtering, journal creation, journal approval/posting/reversal, academic year rollover UI, bank reconciliation, and tax filing remain pending.

## Consequences
Accounting reports now have a usable organization context and basic filters without introducing accounting mutations or financial workflow controls.
