# 0042 Adjustment and Refund Workflow APIs

## Status
Accepted

## Context
Billing adjustment, advance application, and refund services already contain the financial posting behavior. Frontend workflow screens need safe API endpoints that call those services without duplicating accounting logic in serializers or views.

## Decision
Expose service-backed mutation actions for:

- `POST /api/v1/student-advance-balances/apply-to-due/`
- `POST /api/v1/student-advance-balances/apply-to-invoice/`
- `POST /api/v1/billing-discounts/{id}/approve/`
- `POST /api/v1/billing-waivers/{id}/approve/`
- `POST /api/v1/billing-fines/{id}/approve/`
- `POST /api/v1/student-refunds/{id}/approve/`
- `POST /api/v1/student-refunds/{id}/pay/`

Each endpoint validates request shape, enforces API permissions and branch access, then delegates to the relevant billing service. Views do not create journal entries directly.

## Permission Model
The first API layer uses the existing strict `IsFinancialApprover` permission for all adjustment, advance application, and refund mutation actions. That allows Super Admin, Institute Owner, Accountant, or equivalent explicit permission codes. Teachers, Auditors, and Receptionists cannot mutate these workflows.

This is stricter than the future full policy matrix where Branch Admin may approve selected normal adjustments. That policy can be relaxed later after branch approval rules are fully formalized.

## Branch Scope
Object actions resolve target records through branch-scoped querysets. Branch-scoped users with no branch assignment receive no target records. Advance application actions explicitly check target branch access before calling service methods. Super Admin and Institute Owner retain all-branch access.

## Service-Backed Posting
Discounts, waivers, fines, advance applications, and paid refunds continue to post through existing service methods and `AccountingPostingService`. The General Ledger remains the accounting source of truth.

## Refund Limitation
Recognized-revenue refunds remain blocked because the accounting policy is not yet defined. Advance-backed refund payment is supported.

## Pending
Frontend adjustment/refund workflow screens remain pending. Payroll, manual journal, rollover, and other financial mutation APIs are outside this step.
