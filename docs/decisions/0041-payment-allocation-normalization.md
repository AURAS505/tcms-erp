# 0041 Payment Allocation Normalization

## Status
Accepted

## Context
The student payment draft API accepts an allocation array so one payment can be allocated across multiple dues or invoices. The frontend blocks duplicate target selection as a usability safeguard, but backend services must remain safe when clients submit duplicate rows for the same due, invoice, or invoice item.

## Decision
Normalize duplicate allocation targets in `StudentPaymentService.create_draft_payment()` before validation and persistence.

When the same target appears more than once in a draft payload, the service groups allocations by target type and target id, sums their amounts, and stores one `StudentPaymentAllocation` row per unique target. Mixed due and invoice allocations continue to work as separate targets.

The normalized allocation set is then validated against:

- payment amount;
- due or invoice balance;
- required single-target allocation shape;
- existing branch, role, maker-checker, immutability, and posting rules.

## Rationale
Normalizing in the backend keeps the API forgiving while preserving clean storage. It also avoids relying on frontend duplicate blocking for data integrity.

## Scope
This change does not alter payment posting, receipt assignment, journal entry creation, approval permissions, or frontend payment UI behavior. Draft payments still do not create accounting journal entries.

## Pending
There is still no automatic allocation strategy. Frontend duplicate blocking remains a UX convenience, while backend normalization is the authoritative safety net.
