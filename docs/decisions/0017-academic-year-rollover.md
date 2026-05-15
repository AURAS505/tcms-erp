# ADR 0017: Academic Year Rollover

## Status
Accepted

## Context
TCMS ERP needs academic-year rollover that respects Nepali BS academic years and professional double-entry accounting. Closing and opening balances must be ledger-based, auditable, and protected from direct balance edits.

## Decision
1. Add `AcademicYearRolloverService` in `apps/backend/academic/services.py`.
2. Rollover validates:
   - source year belongs to the organization and is active or soft closed,
   - source year is not hard closed,
   - outgoing trial balance is balanced,
   - required accounts `3300` Income Summary and `3200` Retained Earnings exist,
   - target year name is not duplicated,
   - opening entries are not already posted for the rollover.
3. Closing entries:
   - revenue and other income accounts close to Income Summary,
   - expense, contra revenue, and other expense accounts close to Income Summary,
   - Income Summary transfers net income/loss to Retained Earnings.
4. Opening entries:
   - carry forward only asset, contra asset, liability, and equity accounts,
   - do not carry forward revenue or expense accounts,
   - post as system journal entries in the new academic year.
5. The new academic year becomes active and other years become inactive.
6. The outgoing academic year is soft closed, and can be hard closed as part of execution.
7. Executed rollover records, hard-closed academic years, and hard-closed periods are protected from normal edits/deletes.
8. All financial entries use `AccountingPostingService.post_journal_entry()`.

## Audit
Audit logs are recorded for preparation, validation, closing entry posting, opening entry posting, soft close, hard close, activation, cancellation, and execution.

## Not Implemented In This Step
- Rollover APIs.
- Frontend rollover screen.
- PDF/Excel exports.
- Bank reconciliation.
- Tax filing.
- Notification workflow.
- Full Nepali month period generation. `create_new_academic_periods_placeholder()` is intentionally a placeholder.
