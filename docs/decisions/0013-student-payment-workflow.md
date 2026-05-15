# 0013 Student Payment Workflow

## Decision

Implement student payment workflow in service layer with strict draft-vs-posted behavior, maker-checker enforcement, accounting posting on posted payments only, and immutable posted payment records.

## Draft vs Posted Payment

Draft payment creation records collection intent and optional allocation targets but does not update ledger, does not post journals, and does not finalize receipt numbers.

Posting is the financial event. On posting, the system assigns official receipt number, applies allocations to due/invoice balances, updates advance balances for advance receipts, creates and posts journal entry, and writes audit log.

## Maker-Checker Enforcement

Payment creator cannot approve/post the same payment. Approval flow in the payment service checks this before any status transition or ledger impact.

## Accounting Entries

Cash payments post:
- Dr `1110` Cash in Hand
- Cr `1210` Student Receivable

Bank/online/cheque/wallet payments post:
- Dr `1120` Bank Account by default
- Dr `1130` Online Wallet for wallet method
- Cr `1210` Student Receivable

Advance payments post:
- Dr cash/bank/wallet account
- Cr `2210` Student Advance Revenue

The service requires these account codes to exist and raises clear configuration errors when missing.

## Advance Payment Liability Treatment

Advance payments are not recognized as tuition revenue. Posted advance payment increases `StudentAdvanceBalance.received_amount` and `balance_amount`, preserving liability behavior until future application workflow is implemented.

## Receipt Number Strategy

Draft receipt numbers and official receipt numbers are generated separately in the service and are unique per organization through model constraints.

Current implementation uses a simple transaction-protected sequence helper over existing payment records. Future hardening can move this to dedicated sequence tables for stronger high-concurrency guarantees.

## Immutability Controls

Posted/voided/refunded `StudentPayment` records are immutable through normal model save/delete.

Allocations linked to posted/voided/refunded payments are also immutable through normal model save/delete.

## Not Implemented Yet

This step does not implement billing APIs, frontend pages, due generation, discount approval workflow, refund execution workflow, full reversal/void workflow, payroll, teacher earnings, bank reconciliation, or academic year rollover.

## Status

Accepted.
