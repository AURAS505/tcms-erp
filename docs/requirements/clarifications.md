# Required Clarifications

These topics affect money, accounting, academic periods, compliance, or irreversible records. They must be clarified before implementing the related workflow.

## Accounting Policy

- For refunds from recognized revenue, should TCMS debit revenue directly or use a separate refund expense/contra-revenue account?
- What tax rules apply by country, province, or municipality?
- Are discounts treated only as `Discount Allowed`, or are there separate scholarship, promotional, sibling, and hardship accounts?
- Should revenue be recognized on invoice approval, due generation, class delivery, or another policy trigger?
- Are invoice approvals and due generation the same accounting event, or separate operational stages?

## Academic Year and Rollover

- What exact BS month/day starts and ends the academic year for each institute?
- Can different branches have different academic years, or must the organization have one global active year?
- Who can hard-close an academic year?
- Is reopening a soft-closed period allowed? If yes, which roles can do it?

## Billing

- How are partial payments allocated: oldest due first, manual allocation, fee-type priority, or configurable?
- What receipt numbering pattern is required by branch and academic year?
- Are waivers financially equivalent to discounts, or do they require separate approval and accounting?
- Are fines automatically generated, manually approved, or both?

## Payroll

- How is teacher earning calculated for package courses, monthly cut, absences, cancellations, and transfers?
- Are teacher payments branch-scoped or organization-level?
- Do teacher deductions require separate payable or expense accounts?

## Branch and Organization Scope

- Can students transfer between branches?
- Can a teacher serve multiple branches?
- Can an accountant approve transactions across all branches by default, or only when explicitly configured?

## Documents and Audit

- Which manual journals require mandatory document attachment types?
- What is the retention period for sensitive documents?
- Which audit events require IP address and user-agent capture?

## Nepali Dates

- Which BS date conversion library or verified calendar table should be authoritative?
- How far into the past and future must `nepali_calendar_days` be preloaded?

## SaaS Readiness

- Will the first production deployment be single-tenant or multi-tenant?
- Should organization isolation be implemented as shared schema with `organization_id`, separate schemas, or separate databases in future phases?
