# ADR 0016: Financial Reports Foundation

## Status
Accepted

## Context
TCMS ERP requires financial reporting based on the General Ledger as the source of truth. Billing and payroll tables are operational ledgers and must reconcile back to posted accounting entries.

## Decision
1. Add service-layer reports in `apps/backend/accounting/reports.py`.
2. Reports use posted `JournalEntry` records only.
3. Draft, pending, approved-but-unposted, void, and reversed entries do not affect financial reports.
4. Reports support filters for organization, branch, academic year, academic period, AD date range, account, and zero-balance inclusion.
5. Implement:
   - General Ledger
   - Trial Balance
   - Profit and Loss
   - Balance Sheet
   - Cash Flow summary foundation
   - Reconciliation checks

## Report Rules
- General Ledger returns opening balance, period movement, transaction lines, running balance, and closing balance by account.
- Trial Balance reports account-wise debit/credit balances and exposes `is_balanced` plus difference.
- Profit and Loss includes revenue, contra revenue, expenses, other income, and other expenses.
- Balance Sheet includes assets, contra assets, liabilities, equity, and current-year profit/loss as an equity component.
- Cash Flow foundation summarizes ledger movement for `1110`, `1120`, and `1130`.
- Reconciliation compares operational balances against ledger balances for student receivables, teacher payables, and cash accounts where data exists.

## Rationale
- Keeps reporting read-only and ledger-first.
- Provides reusable backend services before APIs and frontend pages.
- Makes reconciliation gaps visible without modifying records.

## Not Implemented In This Step
- Report APIs.
- Frontend report pages.
- PDF/Excel exports.
- Bank statement reconciliation.
- Academic year closing entries or rollover.
- Full IFRS-style cash flow classification.
