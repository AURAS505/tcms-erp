# Financial Workflow Requirements

This document captures the required accounting controls and posting matrix for TCMS ERP. It is a design source only; implementation must wait until the accounting database design is reviewed.

## Accounting Principles

- TCMS ERP must implement proper double-entry accounting.
- General Ledger is the financial source of truth.
- Every financial transaction must generate balanced journal entries.
- Posted journal entries are immutable.
- Corrections must be made through reversal and reposting.
- Closed accounting periods cannot accept postings.
- Hard-closed academic years cannot accept postings.
- Manual journal entries require supporting documents.
- System-generated journal entries must reference source app, model, and record ID.
- Posting must be transaction-safe and use row locks where money can be affected.

## Chart of Accounts Baseline

Assets:

- `1110` Cash in Hand
- `1120` Bank Account
- `1130` Online Wallet
- `1210` Student Receivables
- `1310` Student Advance Payments
- `1400` Fixed Assets

Liabilities:

- `2110` Teacher Payables
- `2210` Student Advance Revenue
- `2300` Taxes Payable
- `2400` Accrued Expenses

Equity:

- `3100` Owner Capital
- `3200` Retained Earnings
- `3300` Income Summary

Revenue:

- `4100` Tuition Fee Revenue
- `4200` Admission Fee Revenue
- `4300` Exam Fee Revenue
- `4400` Fine Income
- `4500` Other Academic Income

Expenses:

- `5100` Teacher Salary Expense
- `5200` Rent Expense
- `5300` Utilities Expense
- `5400` Staff Salary Expense
- `5500` Marketing Expense
- `5600` Office Expense
- `5700` Discount Allowed
- `5800` Bad Debt Expense

## Journal Entry Rules

- A journal entry must have at least two lines.
- Total debit must equal total credit.
- A journal line cannot have both debit and credit.
- A journal line must have either debit or credit.
- Posted entries cannot be edited.
- Reversal entries must reference the original entry.
- Manual entries require supporting documents.
- System entries must reference source app, model, and ID.
- Posting to closed periods must be blocked.
- Posting must run inside database transactions.

## Posting Matrix

| Business event | Debit | Credit |
| --- | --- | --- |
| Fee due or invoice approval | Student Receivable | Tuition Fee Revenue |
| Cash student payment | Cash in Hand | Student Receivable |
| Bank student payment | Bank Account | Student Receivable |
| Advance student payment | Cash or Bank | Student Advance Revenue |
| Advance application | Student Advance Revenue | Student Receivable |
| Discount after invoice | Discount Allowed | Student Receivable |
| Write-off | Bad Debt Expense | Student Receivable |
| Fine | Student Receivable | Fine Income |
| Teacher earning | Teacher Salary Expense | Teacher Payable |
| Teacher payment | Teacher Payable | Cash or Bank |
| Refund from advance | Student Advance Revenue | Cash or Bank |
| Refund from recognized revenue | Tuition Fee Revenue or Refund Expense | Cash or Bank |

Refund treatment for recognized revenue is a required clarification before implementation.

## Academic Year Closing

Closing entries must:

- Debit revenue accounts.
- Credit Income Summary.
- Debit Income Summary.
- Credit expense accounts.
- Transfer net income or loss to Retained Earnings.

New academic year opening must:

- Carry forward assets, liabilities, and equity only.
- Exclude revenue and expense balances.
- Create opening balances using journal entries.
- Keep hard-closed years read-only.
