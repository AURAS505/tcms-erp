# ADR 0015: Payroll Foundation and Teacher Payment Workflow

## Status
Accepted

## Context
Step 14 introduces payroll foundations for teacher earnings and teacher payments with double-entry accounting integration, maker-checker enforcement, auditability, and immutability.

## Decision
1. Add payroll models:
   - `TeacherEarning`
   - `TeacherPaymentBatch`
   - `TeacherPayment`
   - `TeacherPaymentAllocation`
   - `TeacherDeduction`
2. Implement service layer in `apps/backend/payroll/services.py`:
   - `TeacherEarningService`
   - `TeacherPaymentService`
3. Accounting entries:
   - Earning posting: Dr `5100` Teacher Salary Expense / Cr `2110` Teacher Payable
   - Teacher payment posting: Dr `2110` Teacher Payable / Cr cash/bank/wallet account
4. Enforce maker-checker:
   - Earning creator cannot approve same earning.
   - Payment creator cannot approve/post same payment.
5. Enforce immutability:
   - `TeacherEarning`: posted/paid/cancelled/reversed immutable
   - `TeacherPayment`: posted/voided immutable
   - `TeacherPaymentAllocation`: immutable when parent payment posted/voided
   - `TeacherPaymentBatch`: posted immutable
   - `TeacherDeduction`: approved immutable
6. Journal posting always uses `AccountingPostingService.post_journal_entry()`.
7. Account codes are required configuration dependencies and are never auto-created.
8. Audit logs are recorded for earning posting and payment posting.

## Rationale
- Keeps payroll financial effects ledger-first and transaction-safe.
- Prevents silent changes to finalized payroll records.
- Aligns with mandatory maker-checker and audit requirements.
- Establishes stable service boundaries before API/frontend work.

## Consequences
- Payroll posting fails fast if mandatory chart-of-accounts configuration is missing.
- Draft records remain editable; finalized records are protected.
- Future payroll APIs can call services without duplicating accounting logic.

## Not Implemented In This Step
- Payroll API endpoints.
- Frontend payroll pages.
- Automated monthly salary generation.
- Attendance-based salary logic.
- Tax/TDS automation beyond deduction placeholders.
- Bank reconciliation and academic rollover integration.
