# ADR 0026: Frontend Classes Foundation

## Status
Accepted

## Context
Student and guardian read-only frontend foundations are in place. The next operational slice is class administration visibility using existing backend endpoints for subjects, classes, schedules, enrollments, enrollment breaks, enrollment discounts, student withdrawals, and teacher transfers.

## Decision
1. Add read-only list and detail pages for subjects, classes, and class enrollments.
2. Add compact frontend types and API helpers for the full class/enrollment endpoint set.
3. Add sidebar navigation entries for `Classes`, `Subjects`, and `Enrollments`.
4. Keep list pages limited to loading, error, empty, and backend-backed data table states.
5. Keep class and enrollment detail pages read-only with compact detail cards and placeholders for filtered relationship sections.
6. Keep Volt React Dashboard reference-only for general admin spacing, cards, and table feel. No Volt source code, component names, sample data, Bootstrap dependency, or template structure is copied.

## Billing Boundary
Enrollment records are visible, but billing due generation is intentionally excluded. Fee due generation depends on operational workflow rules and accounting boundaries that should be introduced in a separate billing/accounting step.

## Pending
Class create/edit, subject create/edit, enrollment creation, enrollment break approval, enrollment discount approval, withdrawal approval, direct filtered relationship sections, billing, payment, payroll, accounting, charts, and reports remain pending.

## Consequences
The frontend now has the first class/enrollment read-only surface and reusable API coverage for upcoming operational workflows without adding write behavior or finance screens.
