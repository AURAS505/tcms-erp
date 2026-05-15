# ADR 0028: Frontend Billing Read-only Foundation

## Status
Accepted

## Context
Operational read-only foundations now exist for student, guardian, class, enrollment, and teacher modules. Billing visibility is needed next, but payment approval, posting, refund processing, and accounting workflows carry financial risk and require their own maker-checker and audit-focused implementation.

## Decision
1. Add read-only list and detail pages for fee plans, student fee dues, student invoices, and student payments.
2. Add compact frontend types and API helpers for fee plans, fee plan items, dues, invoices, invoice items, payments, allocations, advance balances, discounts, waivers, fines, and refunds.
3. Add sidebar entries for `Billing`, `Fee Plans`, `Dues`, `Invoices`, and `Payments`.
4. Reuse the shared table, page header, loading, error, empty, status, and money display components.
5. Do not expose approve, post, void, refund, discount, waiver, fine, or accounting entry actions.
6. Keep Volt React Dashboard reference-only for general admin spacing, cards, and table feel. No Volt source code, component names, sample data, Bootstrap dependency, or template structure is copied.

## Pending
Payment creation, payment approval, payment posting, voiding, refund processing, discount/waiver/fine approval, filtered invoice items, payment allocations, accounting posting, finance reports, charts, and payroll UI remain pending.

## Consequences
The frontend now provides billing visibility without introducing financial mutations or accounting behavior before the approval and posting rules are implemented.
