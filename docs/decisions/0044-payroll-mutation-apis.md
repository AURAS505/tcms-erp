# 0044 Payroll Mutation APIs

## Status
Accepted

## Context
Payroll services already implement teacher earning and teacher payment workflows with accounting posting, maker-checker checks, audit logging, and immutability. The API layer needs safe service-backed mutation endpoints before frontend payroll mutation UI is built.

## Decision
Expose service-backed payroll mutation actions:

- `POST /api/v1/teacher-earnings/create-manual/`
- `POST /api/v1/teacher-earnings/{id}/approve/`
- `POST /api/v1/teacher-earnings/{id}/post/`
- `POST /api/v1/teacher-payments/create-draft/`
- `POST /api/v1/teacher-payments/{id}/approve/`
- `POST /api/v1/teacher-payments/{id}/post/`
- `POST /api/v1/teacher-payments/{id}/void-placeholder/`

Views validate request shape, enforce API permissions and branch access, then call payroll service methods. Views do not create journal entries directly.

## Permission Model
Payroll mutation actions require the existing strict financial approver policy: Super Admin, Institute Owner, Accountant, or equivalent explicit permission code. Teacher, Receptionist, and Auditor users remain read-only for payroll workflows.

## Branch Scope
Object actions resolve through branch-scoped querysets. Creation actions verify the requested branch before service calls. Branch-scoped users without branch assignments are denied. Super Admin and Institute Owner keep all-branch access.

## Service-Backed Posting
Teacher earning posting remains Dr Teacher Salary Expense / Cr Teacher Payable. Teacher payment posting remains Dr Teacher Payable / Cr Cash/Bank/Wallet. All posting continues through `AccountingPostingService`; the General Ledger remains the source of truth.

## Safety
Direct teacher payment posting now requires approved status, preventing API callers from bypassing approval. Posted payroll records remain immutable and read-only through the API.

## Pending
Frontend payroll mutation UI is not included in this step. Automatic salary generation, manual journal APIs, and rollover APIs remain outside scope.
