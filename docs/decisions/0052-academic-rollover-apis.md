# 0052 Academic Rollover APIs

## Status
Accepted

## Context
Academic year rollover already has service-layer support for trial balance validation, revenue and expense closing entries, balance sheet opening entries, year activation, soft close, hard close, audit logging, and financial immutability. Operators need backend API access before any frontend rollover UI is built.

## Decision
Expose service-backed rollover endpoints:

- `POST /api/v1/academic-year-rollovers/prepare/`
- `POST /api/v1/academic-year-rollovers/{id}/validate/`
- `POST /api/v1/academic-year-rollovers/{id}/execute/`
- `POST /api/v1/academic-year-rollovers/{id}/cancel/`
- `GET /api/v1/academic-year-rollovers/{id}/summary/`
- `POST /api/v1/academic-years/{id}/soft-close/`
- `POST /api/v1/academic-years/{id}/hard-close/`

Views only validate request shape, enforce API permissions, and call `AcademicYearRolloverService`. Closing and opening journal logic remains entirely service-owned and continues to use `AccountingPostingService`.

## Permission Model
Rollover prepare, validate, execute, and cancel require financial/admin roles. Super Admin and Institute Owner have organization-wide access. Accountants may run organization-wide rollover only when they are not branch-scoped by active branch assignments. Branch-scoped users cannot run organization-wide rollover.

Hard close is stricter and requires Super Admin or Institute Owner. Auditors remain read-only; Receptionists and Teachers cannot run rollover or close actions.

## Rollover Behavior
Validation checks required accounts and confirms the outgoing trial balance is balanced. Execution posts closing entries for revenue and expense accounts, posts opening entries for balance sheet accounts, activates the new year, and optionally hard closes the outgoing year.

## Audit And Immutability
The service records audit logs for preparation, validation, closing entries, opening entries, activation, cancellation, execution, and year close actions. Executed rollover records remain immutable. Hard-closed years and periods remain protected from normal edits and block future accounting posting.

## Frontend Status
No frontend rollover UI is added in this step.
