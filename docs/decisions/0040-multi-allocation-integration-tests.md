# 0040 Multi-Allocation Integration Tests

## Status
Accepted

## Context
The frontend now supports drafting a student payment with multiple allocation rows. The backend already accepts multiple allocation objects through the secured draft payment endpoint. Focused test coverage is needed to validate that the API/helper path works with real open dues and invoices without expanding the UI or changing posting logic.

## Decision
Add backend and frontend integration coverage for multi-allocation draft creation.

The backend tests validate that `POST /api/v1/student-payments/create-draft/` can create a draft payment with a due allocation and an invoice allocation, creates allocation records, does not create journal entries, and does not change due or invoice balances until approval/posting.

Negative backend coverage confirms that:

- allocation total greater than payment amount is rejected;
- allocation above a selected due or invoice balance is rejected;
- branch-scoped users cannot create payments for unauthorized branches;
- duplicate allocation targets are currently accepted when their combined amount remains within the target balance.

Frontend helper tests verify that `createDraftStudentPayment()` sends multiple allocation objects using the backend field names.

## Source of Truth
The backend service remains authoritative for allocation validation, branch permissions, maker-checker, immutability, posting, receipt assignment, and accounting side effects. Frontend calculations remain UI feedback only.

## Pending
There is still no automatic allocation strategy. Duplicate target normalization can be revisited later if operations require consolidated allocation lines.
