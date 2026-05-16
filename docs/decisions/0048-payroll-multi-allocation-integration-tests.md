# 0048 Payroll Multi-Allocation Integration Tests

## Status
Accepted

## Context
Teacher payment drafts can allocate one payment across multiple posted or partially paid teacher earnings. The UI validates totals for operator feedback, but payroll correctness depends on backend service validation and posting.

## Decision
Add focused integration coverage for multi-earning teacher payment allocations from API draft creation through approval and posting.

The tests validate that draft creation stores multiple allocation rows without creating accounting journals, and that approval/posting updates each earning balance and posts a payroll payment journal.

## Accounting Behavior
Draft teacher payments must not create journal entries.

Posted teacher payments must create a posted system journal entry with:

- Dr Teacher Payable
- Cr Cash, Bank, or Wallet based on the payment method

## Balance Behavior
Posting applies each allocation to its target earning. Fully paid earnings move to `paid`; earnings with a remaining positive balance move to `partial`.

## Remaining Limitation
Allocation is still manual. There is no automatic payroll allocation strategy by age, period, balance priority, or teacher payroll policy.
