# 0039 Frontend Multi-Allocation Payments

## Status
Accepted

## Context
The student payment draft UI could allocate a payment to only one due or invoice. Real receipts may need to split one payment across multiple dues and invoices while still using the secured service-backed draft payment API.

## Decision
Upgrade the new student payment page to support multiple allocation rows.

Each allocation row can select one open due or invoice and enter an allocation amount. The UI prevents duplicate targets where practical, allows rows to be removed, and shows allocation total, unallocated amount, and payment amount for operator feedback.

Frontend validation blocks draft submission when:

- allocation total exceeds the payment amount;
- an allocation amount is zero or negative;
- an allocation amount exceeds the selected target balance;
- a selected target is duplicated.

Advance payments clear and hide allocation rows and submit without allocations.

## Backend Source of Truth
The frontend calculates UI totals only for feedback and early validation. Backend student payment services remain authoritative for branch scope, allocation validation, payment posting, receipt assignment, due/invoice updates, and accounting effects.

## Limitations
The UI supports manual multi-item allocation only. Automatic allocation, discount/waiver/fine/refund workflows, payroll workflows, and accounting journal UI are still out of scope.
