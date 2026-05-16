# 0037 Student-Filtered Open Obligations API

## Status
Accepted

## Context
The frontend payment allocation picker initially loaded general due and invoice pages, then filtered the loaded page by student. That was usable for a small dataset but inefficient and incomplete for larger payment operations.

## Decision
Extend the existing read-only billing endpoints with student-filtered open-obligation query parameters:

- `GET /api/v1/student-fee-dues/?student=<id>&open_only=true`
- `GET /api/v1/student-invoices/?student=<id>&open_only=true`

The endpoints also support the existing organization, branch, academic year, and status filters, plus an academic period filter.

Open obligations include:

- `approved`
- `unpaid`
- `partial`

Open obligation queries exclude draft, paid, cancelled, and written-off records, and also require a positive visible balance.

## Branch Scope
The filters run after the shared branch-scoped queryset rules. Branch-scoped users only see obligations from assigned branches. Branch-scoped users without active branch assignments receive no branch records. Super Admin and Institute Owner users retain all-branch read access.

## Frontend Use
The payment allocation picker should call these filtered endpoints after a student is selected, instead of loading a generic page of dues/invoices and filtering client-side. The frontend remains a convenience layer; backend payment services remain the source of truth for allocation validation and posting.

## Out of Scope
This step does not add payment posting changes, mutation APIs, multi-item allocation UX, discount/waiver/fine/refund workflows, payroll workflows, or accounting journal UI.
