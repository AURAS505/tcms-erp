# ADR 0014: Advance Application, Billing Adjustments, and Refund Workflows

## Status
Accepted

## Context
Step 13 extends billing workflow after student payment posting. We need service-layer workflows for:
- applying advance balances to dues/invoices,
- approving discounts, waivers/write-offs, and fines,
- processing advance-backed refunds,
with strict double-entry posting, maker-checker checks, audit logging, and immutable posted effects.

## Decision
1. Implement service-layer workflows in `apps/backend/billing/services.py`:
   - `AdvanceApplicationService`
   - `BillingAdjustmentService`
   - `StudentRefundService`
2. All financial effects post through `AccountingPostingService.post_journal_entry()`.
3. Required chart-of-accounts codes are configuration dependencies and are never auto-created:
   - `1110` Cash in Hand
   - `1120` Bank Account
   - `1130` Online Wallet
   - `1210` Student Receivable
   - `2210` Student Advance Revenue
   - `4400` Fine Income
   - `5700` Discount Allowed
   - `5800` Bad Debt Expense
4. Accounting postings:
   - Advance application: Dr `2210` / Cr `1210`
   - Discount approval: Dr `5700` / Cr `1210`
   - Waiver/write-off approval: Dr `5800` / Cr `1210`
   - Fine approval: Dr `1210` / Cr `4400`
   - Advance refund payment: Dr `2210` / Cr cash/bank
5. Refund from recognized revenue is blocked by policy guard if accounting policy is not configured.
6. Approved/paid adjustment records are immutable through normal model operations:
   - approved `BillingDiscount`
   - approved `BillingWaiver`
   - approved `BillingFine`
   - paid `StudentRefund`
7. Each approval/posting workflow creates audit events.

## Rationale
- Keeps all financial mutations in backend services with transaction safety.
- Enforces ledger-first accounting design.
- Prevents silent mutation of finalized financial effects.
- Keeps policy-sensitive refund treatment explicit and safe.

## Consequences
- Billing workflows fail fast when required accounts are missing.
- Recognized-revenue refund remains intentionally unavailable until policy is formally defined.
- Future API endpoints can call these services directly without duplicating accounting logic.

## Not Implemented In This Step
- Billing API endpoints and frontend pages.
- Full payment void/reversal workflow.
- Bank reconciliation workflow.
- Academic year rollover execution.
- Revenue-refund accounting policy automation.
