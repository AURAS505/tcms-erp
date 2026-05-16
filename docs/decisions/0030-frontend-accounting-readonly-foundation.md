# ADR 0030: Frontend Accounting Read-only Foundation

## Status
Accepted

## Context
Operational, billing, and payroll read-only frontend foundations are in place. Accounting visibility is needed for chart of accounts, journal entries, supporting documents, and core reports, but accounting mutations require strict approval, posting, reversal, rollover, and audit controls.

## Decision
1. Add read-only list and detail pages for chart of accounts and journal entries.
2. Add a read-only accounting documents list page.
3. Add read-only report pages for trial balance, general ledger, profit and loss, and balance sheet.
4. Add compact frontend types and API helpers for accounts, journal entries, journal lines, documents, and report payloads.
5. Require report filters through query parameters, including `organization`, instead of inventing frontend mock state.
6. Do not expose manual journal creation, approval, posting, reversal, deletion, rollover, reconciliation, or accounting mutation actions.
7. Keep Volt React Dashboard reference-only for general admin spacing, cards, and table feel. No Volt source code, component names, sample data, Bootstrap dependency, or template structure is copied.

## Pending
Manual journal entry creation, maker-checker approval, posting, reversal, rollover execution, bank reconciliation, tax filing, filtered journal line embedding, report filter forms, exports, and accounting mutation workflows remain pending.

## Consequences
The frontend can now inspect accounting records and reports without weakening the backend accounting control model or adding financial mutation behavior prematurely.
