# 0006 Academic Module Foundation

## Decision

Create the academic foundation before billing, accounting, student, class, and rollover workflows.

## Scope

Step 5 adds:

- `AcademicYear`
- `AcademicPeriod`
- `NepaliCalendarDay`
- `AcademicYearRollover`
- Django admin registrations
- Initial model tests
- Initial academic migration

## Nepali BS Date Strategy

TCMS ERP is BS-calendar first for user-facing academic and billing workflows. Academic years, academic periods, and calendar days store BS date strings and BS year/month/day fields so the UI, billing periods, and reports can use Nepali dates directly.

The actual BS/AD conversion algorithm is not implemented in this step. `NepaliCalendarDay` is the future authoritative mapping table once a verified Nepali calendar source is selected.

## Why AD Dates Are Also Stored

AD dates are stored alongside BS dates for database sorting, date range filtering, integrations, scheduling, and operational consistency. This avoids relying on text-only BS dates for backend comparisons and external systems.

## One-Active-Year Rule

Only one academic year can be active per organization. This is enforced with a conditional database constraint on `AcademicYear.is_active`. Future workflows must keep hard-closed years read-only and preserve operational history for reporting.

## Academic Period Role

Academic periods represent the monthly or reporting periods inside an academic year. They are needed for future BS-month billing, accounting period close states, financial reports, and period-based posting restrictions. This step stores period status only; it does not enforce posting rules.

## Rollover Placeholder

`AcademicYearRollover` stores future rollover state: validation status, trial balance validation, revenue/expense closing completion, opening balance posting, executor, and execution timestamp. Actual financial rollover is not implemented because it depends on accounting models, closing entries, trial balance validation, and clarification of period/year close authority.

## Constraints

This step does not implement billing due generation, accounting posting, financial rollover execution, student/class/teacher/payroll models, frontend pages, APIs, or BS/AD conversion logic.

## Status

Accepted.
