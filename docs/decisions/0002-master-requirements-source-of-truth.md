# 0002 Master Requirements Source of Truth

## Decision

Persist the master TCMS ERP requirements in repository documentation under `docs/requirements`, `docs/accounting`, and `docs/architecture`.

## Context

The initial workspace contained no SOP files, legacy source documents, README files, old code archives, or formal requirement documents. The master prompt supplied for TCMS ERP is therefore the current source of truth.

## Consequences

- Future implementation steps must check these documentation files before writing production code.
- Financial, tax, rollover, revenue recognition, refund, discount, teacher earning, and period closing logic must not be assumed when unclear.
- Clarification questions are tracked in `docs/requirements/clarifications.md`.

## Status

Accepted.
