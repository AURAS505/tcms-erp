# 0046 Frontend Teacher Earning Picker

## Status
Accepted

## Context
The first teacher payment draft UI accepted a manual teacher earning ID for allocation. That was service-safe because the backend validated the allocation, but it was easy for users to mistype or select the wrong earning.

## Decision
Replace manual teacher earning ID entry with a posted-earning picker on `/dashboard/payroll/payments/new`.

The picker loads teacher earnings after a teacher is selected and requests `open_only=true`, which returns only posted or partial earnings with positive balance. Users can inspect earning date, period label, status, net amount, paid amount, and balance before selecting an earning.

## Backend Source Of Truth
Frontend validation blocks non-positive allocations and amounts above the selected earning balance for usability. The backend remains the final authority for branch scope, teacher scope, earning status, balance, maker-checker, immutability, and accounting posting.

## Current Limitation
This step supports a single earning allocation per draft teacher payment. Multi-earning allocation remains possible later by extending the picker to support multiple selected rows.

## Volt Reference
The Volt dashboard prompt remains reference-only for visual direction. No Volt source code is copied.

## Out Of Scope
Accounting journal UI, academic rollover UI, automatic salary generation, attendance-based payroll, and accounting calculations remain outside this step.
