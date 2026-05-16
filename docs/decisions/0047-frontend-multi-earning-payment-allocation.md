# 0047 Frontend Multi-Earning Payment Allocation

## Status
Accepted

## Context
The teacher payment draft UI used a posted-earning picker, but it supported only one earning allocation. A single payroll disbursement often needs to settle more than one posted or partially paid earning for the same teacher.

## Decision
Allow `/dashboard/payroll/payments/new` to allocate one teacher payment across multiple open teacher earnings.

Each allocation row selects one posted/unpaid teacher earning and an allocation amount. The UI prevents duplicate earning selections where practical, allows removing rows, and shows payment amount, allocation total, and unallocated amount for operator feedback.

## Backend Source Of Truth
The frontend calculates allocation totals only for usability. The backend remains responsible for branch scope, teacher scope, earning status, balance validation, maker-checker, immutability, and accounting posting.

## Remaining Limitations
The allocation remains manual. The UI does not auto-allocate by age, period, or balance priority, and it does not create or inspect accounting journals.

## Volt Reference
The Volt dashboard prompt remains reference-only for visual direction. No Volt source code is copied.
