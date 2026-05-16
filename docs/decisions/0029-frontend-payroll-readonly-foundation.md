# ADR 0029: Frontend Payroll Read-only Foundation

## Status
Accepted

## Context
The frontend now has read-only operational and billing visibility. Payroll visibility is needed for teacher earnings and payments, but teacher payment processing, payroll approvals, and accounting posting require separate maker-checker and audit-focused workflows.

## Decision
1. Add read-only list and detail pages for teacher earnings, teacher payment batches, and teacher payments.
2. Add compact frontend types and API helpers for teacher earnings, payment batches, payments, payment allocations, and deductions.
3. Add sidebar entries for `Payroll`, `Teacher Earnings`, `Teacher Payments`, and `Payment Batches`.
4. Reuse shared table, page header, loading, error, empty, status, and money display components.
5. Do not expose create, approve, post, pay, void, deduction approval, or accounting entry actions.
6. Keep Volt React Dashboard reference-only for general admin spacing, cards, and table feel. No Volt source code, component names, sample data, Bootstrap dependency, or template structure is copied.

## Pending
Teacher payment creation, approval, posting, voiding, deduction approval, filtered allocations, accounting posting, finance reports, charts, and payroll mutation workflows remain pending.

## Consequences
The frontend can now show payroll records from the backend without introducing financial mutation or posting behavior before controls are implemented.
