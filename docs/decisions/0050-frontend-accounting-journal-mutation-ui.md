# 0050 Frontend Accounting Journal Mutation UI

## Status
Accepted

## Context
Backend accounting mutation APIs now support manual journal draft creation, approval, posting, reversal, and simple document references. Operators need UI access to those workflows without duplicating accounting rules in the browser.

## Decision
Add accounting journal mutation UI focused on manual journal workflows.

`/dashboard/accounting/journal-entries/new` creates balanced manual draft journals. The page lets accounting users enter header fields and journal lines, add or remove line rows, and view debit total, credit total, and difference before submission.

Journal detail pages expose backend actions for approval, posting, and reversal when the journal status and user role allow them.

## Backend Source Of Truth
The frontend calculates debit and credit totals only for operator feedback and to avoid obvious invalid submissions. Backend services remain responsible for account validation, double-entry validation, branch scope, maker-checker, closed-period protection, posting, reversal, immutability, and audit logging.

## Role Gating
Mutation actions are visible only to Super Admin, Institute Owner, and Accountant roles. Receptionist, Teacher, and Auditor roles retain read-only accounting access.

## Read-Only States
Posted, reversed, and void journals are presented as read-only. Posted journals may show the reversal action for accounting roles; reversal calls the backend reversal endpoint and does not edit the original journal.

## Remaining Limitations
Document reference creation is supported by API helpers but no full upload UI is implemented. There is no bank reconciliation, tax filing, academic rollover, or accounting policy automation in this step.

## Volt Reference
The Volt dashboard prompt remains reference-only for visual direction. No Volt source code is copied.
