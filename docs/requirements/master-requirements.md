# TCMS ERP Master Requirements

This document records the master requirements supplied for TCMS ERP and is the repository-level source of truth until more formal SOPs, signed specifications, or legacy system documents are added.

## Product Vision

TCMS ERP is a professional enterprise-grade full-stack education management system for:

- Schools
- Colleges
- Coaching institutes
- Tuition centers
- Multi-branch education businesses

The system must support student operations, academic management, billing, payroll, accounting, reporting, branch isolation, auditability, and future SaaS scalability.

## Core Product Goals

- Student admission and lifecycle management
- Guardian and parent management
- Teacher management
- Class, batch, subject, and enrollment management
- Fee plan and due generation
- Student payments, advance payments, discounts, waivers, fines, and refunds
- Teacher earnings and teacher payments
- Professional double-entry accounting
- Chart of accounts, journals, ledger, trial balance, P&L, balance sheet, and cash flow
- Bank reconciliation
- Academic year rollover
- Nepali BS dates throughout the user interface
- AD/Gregorian storage where required for consistency and integrations
- Branch-level data isolation
- Role-based access control
- Maker-checker financial approval workflow
- Audit logs
- Reports and exports
- Backup and disaster recovery readiness
- Future SaaS and multi-branch scalability

## Mandatory Business Rules

- All permission checks must be enforced in the backend.
- Frontend hiding is not security.
- Branch Admins and Receptionists can only access assigned branch data.
- Super Admin and Institute Owner can access all branches.
- Accountant access can be branch-scoped or organization-wide depending on configuration.
- Maker-checker is mandatory for all financial transactions.
- The creator of a financial transaction cannot approve the same transaction.
- Financial records must not be edited or deleted after posting.
- Corrections must be performed by reversal and reposting.
- Posted journal entries are immutable.
- Closed accounting periods cannot accept new postings.
- Hard-closed academic years cannot accept postings under any circumstance.
- Only one academic year can be active at a time.
- Operational history from all academic years must remain searchable and reportable.
- Financial year transfer must carry forward only balance sheet accounts.
- Revenue and expense accounts must close to zero during academic year rollover.
- General Ledger is the financial source of truth.
- Billing and payroll reports are operational reports and must reconcile to ledger.
- Advance student payments are liabilities, not revenue.
- Student receivable is debited when fees are earned or invoiced.
- Cash or bank is debited when money is received.
- Teacher earnings create Teacher Salary Expense and Teacher Payable.
- Teacher payment reduces Teacher Payable.
- Every financial transaction must create balanced journal entries.
- Total debit must always equal total credit.
- Manual journals require supporting documents.
- Sensitive actions must create audit logs.
- Money must never use floating point.
- Money must use decimal fields.
- Receipts, vouchers, journal numbers, and admission numbers are immutable once finalized.

## User Roles

Initial role model:

- Super Admin
- Institute Owner
- Branch Admin
- Accountant
- Receptionist
- Teacher
- Student or Guardian portal user, when portal features are introduced
- Auditor or read-only finance reviewer, when audit workflows are introduced

Roles must be backed by permission records and enforced on the backend.

## Backend Modules

- `accounts`: custom user model, roles, permissions, branch assignment, password reset, sessions, maker-checker helpers
- `organizations`: organization profile, branches, settings, approval matrix, tax settings
- `academic`: academic years, periods, Nepali calendar mapping, rollover, period close states
- `students`: inquiry, admission workflow, profile, documents, academic history, lifecycle status
- `guardians`: guardians, families, student-guardian relationships
- `teachers`: teacher profile, contracts, activities, payment model configuration
- `classes`: rooms/classes, batches, sections, subjects, schedules, enrollments, breaks, discounts, withdrawals, transfers
- `billing`: fee plans, dues, invoices, payment drafts, approvals, allocations, discounts, waivers, fines, refunds, advance payments
- `payroll`: earning models, teacher earnings, payment batches, allocations, deductions
- `accounting`: chart of accounts, journals, ledger, reports, periods, opening/closing/reversal entries, bank reconciliation, tax, audit trail
- `reports`: operational and financial reports, exports
- `notifications`: future notification workflows
- `files`: private documents and supporting attachments
- `common`: base models, UUIDs, timestamps, soft delete, money utilities, date utilities, permissions, pagination, audit helpers

## Frontend Requirements

The frontend must provide:

- Login and forgot password
- Dashboard
- Student inquiry, admission, and profile
- Guardian profile
- Teacher profile
- Class and enrollment workflows
- Fee dues, payment draft, payment approval, receipt screen
- Advance payments, discounts, waivers, refunds
- Teacher earnings and payment workflows
- Chart of accounts, journal entry, ledger, trial balance, P&L, balance sheet, cash flow
- Academic year rollover screen
- Bank reconciliation
- Audit log viewer
- Reports
- Settings
- User and role management

Frontend rules:

- Use strict TypeScript.
- Use Zod for form validation.
- Use React Hook Form for forms.
- Use TanStack Query for API data.
- Do not calculate final financial amounts in frontend.
- Backend is the source of truth for all financial calculations.
- Show BS dates prominently.
- Allow AD fallback only where useful.
- Use permission-based navigation, backed by backend authorization.
- Provide clear empty, loading, error, and success states.
- Use reusable accessible components.

## API Requirements

Use REST APIs with consistent response envelopes.

Successful response:

```json
{
  "success": true,
  "data": {},
  "message": "",
  "errors": null,
  "meta": {}
}
```

Validation error response:

```json
{
  "success": false,
  "message": "Validation failed",
  "errors": {
    "field_name": ["error message"]
  }
}
```

Representative endpoint patterns:

- `GET /api/students/`
- `POST /api/students/`
- `GET /api/students/{id}/`
- `PATCH /api/students/{id}/`
- `POST /api/students/{id}/submit-for-approval/`
- `POST /api/students/{id}/approve/`
- `POST /api/billing/generate-dues/`
- `POST /api/billing/payments/`
- `POST /api/billing/payments/{id}/approve/`
- `POST /api/billing/refunds/{id}/approve/`
- `POST /api/payroll/teacher-payments/{id}/approve/`
- `POST /api/accounting/journal-entries/{id}/approve/`
- `POST /api/accounting/journal-entries/{id}/post/`
- `POST /api/accounting/journal-entries/{id}/reverse/`
- `GET /api/accounting/general-ledger/`
- `GET /api/accounting/trial-balance/`
- `GET /api/accounting/profit-and-loss/`
- `GET /api/accounting/balance-sheet/`
- `GET /api/accounting/cash-flow/`
- `POST /api/academic/rollover/prepare/`
- `POST /api/academic/rollover/validate/`
- `POST /api/academic/rollover/execute/`

## Security Requirements

- Backend permission enforcement
- Branch data isolation
- CSRF protection for cookie auth
- Secure HTTP-only cookies
- Login and password reset rate limiting
- Hashed password reset tokens
- Private sensitive files
- File type and size validation
- Audit logs for sensitive actions
- IP address and user-agent capture for audit events
- No committed secrets
- `.env.example` only
- CORS restricted to known frontend origins
- Encrypted database backups
- Production debug disabled
- Strong password policy
- Optional future 2FA architecture

## Testing Requirements

Backend:

- pytest
- pytest-django
- factory_boy
- coverage

Frontend:

- Vitest
- React Testing Library
- Playwright for critical flows

Mandatory financial tests:

- Due generation posts Dr Student Receivable / Cr Revenue.
- Cash payment posts Dr Cash / Cr Student Receivable.
- Bank payment posts Dr Bank / Cr Student Receivable.
- Partial payment leaves correct balance.
- Advance payment posts as liability.
- Advance application reduces liability and receivable correctly.
- Discount after invoice posts to Discount Allowed.
- Fine posts Dr Student Receivable / Cr Fine Income.
- Teacher earning posts Dr Teacher Salary Expense / Cr Teacher Payable.
- Teacher payment posts Dr Teacher Payable / Cr Cash or Bank.
- Payment void creates reversal and does not delete original.
- Closed period blocks posting.
- Trial balance always balances.
- Reports reconcile to ledger totals.
- Maker-checker prevents self-approval.
- Branch user cannot access other branch records.
- Hard-closed academic year blocks all posting.
- Academic year rollover carries only balance sheet accounts.
- Revenue and expense accounts start at zero in new academic year.

## DevOps Requirements

Local development services:

- backend
- frontend
- postgres
- redis
- celery_worker
- celery_beat
- nginx optional

Required infrastructure artifacts:

- `docker-compose.yml`
- backend Dockerfile
- frontend Dockerfile
- `.env.example`
- `Makefile`
- `README.md`

CI/CD pipeline should include:

- Backend lint
- Backend tests
- Backend migration check
- Frontend lint
- Frontend type check
- Frontend tests
- Docker image build
- Smoke tests
- Staging deployment
- Manual approval for production
- Production deployment
- Post-deployment smoke tests

## Backup Requirements

- Daily PostgreSQL full dump retained for 30 days.
- PostgreSQL WAL/PITR retained for 7 days.
- Daily media backup retained for 90 days.
- Weekly full snapshot retained for 6 months.
- Monthly archive retained for 7 years.
- Quarterly restore drill is mandatory.

## Coding Standards

- Use clean architecture.
- Keep views thin.
- Place business logic in service classes/functions.
- Use database transactions for financial workflows.
- Use `select_for_update` where race conditions can affect money.
- Never duplicate financial posting logic.
- Centralize accounting posting in `AccountingPostingService`.
- Centralize audit logging in `AuditLogService`.
- Centralize permission checks.
- Use typed frontend code.
- Avoid implicit `any` in TypeScript.
- Backend and frontend validation should both exist.
- Backend validation is authoritative.
- Every financial service must have tests.
- Every permission-sensitive API must have tests.
- Every model must have readable string representation.
- Use clear naming.
- Comments should explain business logic or financial reasoning.
- Avoid overengineering while preserving future SaaS and microservice migration options.
