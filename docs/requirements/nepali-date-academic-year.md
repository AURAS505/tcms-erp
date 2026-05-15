# Nepali Date and Academic Year Requirements

## User Interface Date Rules

- User-facing dates must display Nepali BS dates by default.
- AD/Gregorian fallback may be shown where useful.
- Billing periods are based on Nepali months.
- Dues normally generate on the first day of each Nepali month.
- Payment due rules may use fixed BS dates or end-of-BS-month rules.
- Reports must support BS date range filters.
- Reports should also support AD date range filters where needed for integrations, sorting, and reconciliation.

## Storage Rules

- Backend should store AD/Gregorian dates where needed for database consistency, sorting, scheduling, and integrations.
- Store both BS and AD date values where business logic depends on Nepali calendar periods.
- Academic years are BS-year based.

## Academic Year Rules

- Only one academic year can be active at a time.
- Operational records from all academic years must remain accessible.
- Finance rollover must transfer closing balance sheet balances to the next academic year.
- Revenue and expense accounts must not carry forward as active balances.
- Outgoing academic year must be reconciled before rollover.
- Trial balance must be balanced before rollover.
- Closing entries must be posted before new-year opening entries.
- New academic year opening balances must be journal entries, not plain data fields.
- Hard-closed years must become read-only.
- Reports must be filterable by academic year, branch, BS date range, AD date range where needed, and accounting period.
