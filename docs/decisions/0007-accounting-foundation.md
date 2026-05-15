# 0007 Accounting Foundation

## Decision

Create the base double-entry accounting structure before billing, payroll, payments, teacher earnings, bank reconciliation, and rollover execution.

## Scope

Step 6 adds:

- `Account`
- `JournalEntry`
- `JournalEntryLine`
- `AccountingDocument`
- `LedgerSnapshot` placeholder
- `AccountingPostingService`
- Django admin registrations
- Initial accounting tests
- Initial accounting migration

## Chart of Accounts Design

`Account` stores organization-scoped chart of accounts records. Account codes are unique per organization and support parent-child grouping, account type, normal balance, system-account flag, active flag, and description. System-account immutability and inactive-account posting restrictions are expected in future service layers.

## Double-Entry Model

`JournalEntry` stores the journal header and `JournalEntryLine` stores debit and credit lines. Each line must have exactly one side: either debit or credit. Negative amounts are blocked. The posting service validates that a journal has at least two lines and that total debits equal total credits.

## Journal Entry Design

Journal entries are organization-scoped, optionally branch-scoped, tied to an academic year, optionally tied to an academic period, and prepared for source references from future modules. Entry numbers are unique per organization. Created, approved, posted, and reversal user references prepare the model for maker-checker workflows, but approval enforcement is not implemented in this step.

## Why Billing and Payroll Posting Are Deferred

Billing, payroll, student payment, teacher payment, refund, and tax posting flows require their own domain models and clarified policy choices. This step only creates the accounting substrate and safe generic posting validation.

## Immutability Expectations

Posted journal entries must become immutable in future steps. Corrections must be made through reversal and reposting. This step records status, posted timestamp, reversed-entry reference, and document references, but full immutability enforcement belongs in the next audit/immutability hardening step.

## Academic Period Relationship

Journal entries reference academic years and may reference academic periods. Posting is blocked if the academic year or period is hard-closed. Softer period-close behavior remains a future policy and workflow decision.

## Constraints

This step does not implement student fee dues, student payments, teacher earnings, teacher payments, billing/payroll accounting flows, academic year rollover execution, tax calculations, bank reconciliation, frontend pages, or accounting APIs.

## Status

Accepted.
