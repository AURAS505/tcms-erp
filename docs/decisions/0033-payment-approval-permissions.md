# 0033 Payment Approval Permissions

## Status
Accepted

## Context
Student payment mutation APIs were introduced as service-backed endpoints. Approval and posting affect dues, receipts, and the general ledger, so these endpoints need backend role enforcement before frontend mutation screens are built.

## Decision
Add backend permission helpers for role and permission-code checks, then apply payment-specific permissions to student payment workflow actions.

Draft payment creation is allowed for:

- Super Admin
- Institute Owner
- Branch Admin
- Accountant
- Receptionist

Payment approval/posting is allowed for:

- Super Admin
- Institute Owner
- Accountant

Auditors remain read-only. Teachers cannot create or approve student payments.

## Enforcement
`StudentPaymentViewSet` now applies action-specific permissions:

- `list` and `retrieve` continue to use the existing authenticated branch-scoped foundation.
- `create-draft` requires `IsPaymentDraftCreator`.
- `approve` requires `IsFinancialApprover`.
- `void-placeholder` also requires `IsFinancialApprover`.

Frontend navigation or button hiding is not treated as security. Backend permissions are mandatory for payment mutation actions.

## Maker-Checker
Maker-checker remains enforced in `StudentPaymentService`. Even an accountant, owner, or super-admin cannot approve/post a payment they created.

## Branch Scope
Read operations continue to use the existing branch-scoped queryset and object permission foundation. Custom mutation actions require authenticated role permission now; deeper branch-scope enforcement inside workflow actions remains a pending hardening item.

## Not Included
This step does not add frontend payment UI and does not expose discount, waiver, fine, refund, payroll, accounting, reversal, or rollover mutation APIs.
