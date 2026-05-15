# 0012 Billing Foundation

## Decision

Create billing data foundations before due generation services, payment approval, receipt sequencing, accounting posting, APIs, and frontend screens.

## Billing Data Design

The billing module now represents fee plans, fee plan items, student fee dues, invoices, invoice items, draft student payments, payment allocations, student advance balances, discounts, waivers, fines, and refunds.

All money fields use Decimal storage. Stored amount and balance fields have non-negative validation and database check constraints where practical.

## Fee Due vs Invoice vs Payment

Fee dues represent operational receivables for a student, class enrollment, academic period, and fee plan. They are the basis for future billing generation and aging reports.

Invoices group one or more fee dues or charge lines into an invoice document with an invoice number and invoice-level totals.

Payments represent draft or later-approved receipts of money. This step stores payment draft data and allocation records only. It does not approve, post, assign final receipt numbers, or create journal entries.

## Advance Payment Concept

Student advance balances are modeled separately because advance payments are liabilities until applied to receivables. Actual liability posting to Student Advance Revenue is deferred to the payment workflow and accounting posting steps.

## Discount, Waiver, Fine, and Refund

Billing discounts store scholarship, sibling, merit, hardship, one-time, bulk, and other discount requests.

Waivers are represented separately because their approval and accounting treatment may differ from standard discounts and require policy clarification.

Fines are represented separately from fee dues so late fees and penalties can be reviewed before becoming approved receivables.

Refunds store refund requests and voucher references, but do not pay cash/bank or post accounting entries in this step.

## Why Accounting Posting Is Deferred

Due approval, payment approval, advance application, discounts, fines, write-offs, and refunds all affect the ledger. The exact revenue recognition, waiver accounting, receipt sequencing, and refund policy still require later workflow implementation through the centralized accounting posting service.

## BS/AD Date Handling

Billing records store AD dates for sorting, reconciliation, and integrations and BS date strings for Nepali user-facing workflows. Billing periods remain tied to academic periods and Nepali month labels.

## Constraints

This step does not implement due generation, payment approval, receipt sequence generation, accounting posting, teacher earnings, payroll, billing APIs, frontend pages, notifications, or bank reconciliation.

## Status

Accepted.
