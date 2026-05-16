# 0043 Frontend Adjustment and Refund Workflows

## Status
Accepted

## Context
Step 21D exposed service-backed backend APIs for advance application, billing adjustment approval, and advance-backed refund approval/payment. The frontend needs compact action surfaces without duplicating accounting behavior or building unrelated finance workflows.

## Decision
Add read/write billing pages for:

- advance balances;
- billing discounts;
- billing waivers/write-offs;
- billing fines;
- student refunds.

The pages reuse existing billing table, status, money, search, loading, empty, and error components. Mutation actions call only the service-backed backend endpoints:

- advance application to due/invoice;
- discount approval;
- waiver/write-off approval;
- fine approval;
- refund approval;
- refund payment.

## Role Gating
Mutation controls are visible only to Super Admin, Institute Owner, and Accountant roles. Receptionist, Teacher, and Auditor users see read-only records only. Approved adjustments and paid/cancelled refunds do not show mutation actions.

## Source of Truth
The frontend does not calculate accounting effects. Backend services remain authoritative for validation, posting, branch scope, maker-checker, immutability, and recognized-revenue refund policy.

## Known Limitations
Advance application uses a compact ID-based form rather than a full due/invoice picker. Recognized-revenue refunds may be rejected by backend policy. Branch Admin approval remains intentionally stricter until the backend policy matrix is relaxed.

## Volt Reference
Volt remains visual reference only for compact dashboard spacing, table/card shape, and admin UI tone. No Volt source code, component names, or sample data were copied.
