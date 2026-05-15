# 0003 Backend Common Utilities

## Decision

Create reusable backend utilities in the `common` Django app before implementing domain modules.

## Scope

Step 2 adds:

- Abstract UUID, timestamp, user audit, active status, and soft-delete model mixins
- Decimal-safe money helpers
- API response envelope helpers
- Standard pagination placeholder
- Common exception classes
- Common validation helpers
- Nepali date placeholder interfaces
- Audit context placeholder for future request/user tracking
- Focused tests for common utility behavior

## Constraints

This step intentionally does not add business modules, accounting tables, billing workflows, authentication, custom users, permissions, or financial posting logic.

## Rationale

Future modules need consistent identifiers, audit fields, soft-delete behavior, Decimal-safe money handling, response envelopes, and date interfaces. Defining these foundations early reduces duplication while keeping business logic out of the common layer.

## Status

Accepted.
