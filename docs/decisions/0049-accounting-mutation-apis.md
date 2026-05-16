# 0049 Accounting Mutation APIs

## Status
Accepted

## Context
Accounting reports are ledger-first and read only, but operators need safe backend workflows for manual journal entries, approval, posting, reversal, and document references before any frontend mutation UI is built.

## Decision
Expose service-backed journal mutation actions:

- `POST /api/v1/journal-entries/create-manual/`
- `POST /api/v1/journal-entries/{id}/approve/`
- `POST /api/v1/journal-entries/{id}/post/`
- `POST /api/v1/journal-entries/{id}/reverse/`
- `POST /api/v1/journal-entries/{id}/documents/`

Views and serializers validate request shape and permissions, then delegate accounting behavior to the service layer. Posting continues to go through `AccountingPostingService`.

## Workflow
Manual journal creation stores a balanced draft with at least two lines. Draft and approved journals do not affect reports.

Approval is separate from posting and enforces maker-checker: the creator cannot approve the same journal.

Posting requires an approved journal and uses `AccountingPostingService.post_journal_entry()`, which validates line count, double-entry balance, and hard-closed academic year or period rules.

Reversal creates a new opposite posted journal entry that references the original through `reversed_entry`. The original posted journal remains immutable and posted so the General Ledger shows both the original and reversing entry.

## Permissions And Branch Scope
Mutation actions require financial roles: Super Admin, Institute Owner, or Accountant. Auditors remain read-only; Receptionists and Teachers cannot mutate accounting.

Branch-scoped users can create or mutate only journals in assigned branches. Users without branch assignment are denied for branch-scoped journal mutations.

## Immutability And Audit
Posted, reversed, and void journal entries and their lines remain protected from direct mutation or deletion. Accounting mutation services create audit logs for manual creation, approval, posting, reversal, and document attachment.

## Frontend Status
No frontend accounting mutation UI is added in this step. Existing accounting pages remain read-only for journal mutation workflows.
