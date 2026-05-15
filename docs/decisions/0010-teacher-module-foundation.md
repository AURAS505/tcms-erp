# 0010 Teacher Module Foundation

## Decision

Create teacher data foundations before class assignment, payroll, teacher earning recognition, teacher payment workflows, accounting posting, and frontend screens.

## Teacher Profile Design

The teacher module stores organization-scoped and branch-scoped teacher profiles with an immutable-per-organization employee number, contact details, qualification, specialization, joining dates, optional future user-account link, and lifecycle status.

The optional user link allows a future teacher portal without requiring every teacher profile to be a login user at creation time.

## Teacher Contract Design

Teacher contracts store the earning model configuration that future payroll services will consume. Contracts are linked to teacher, organization, branch, and optionally academic year. Only one active contract per teacher per academic year is allowed where the academic year is set.

## Earning Models

Three earning models are represented:

- Monthly cut percentage: teacher share is based on a percentage of eligible collected or earned fees, depending on the future clarified payroll policy.
- Package course: teacher compensation is based on a package amount for a course or batch.
- Fixed monthly salary: teacher compensation is a fixed monthly amount.

The models intentionally store configuration only. They do not calculate earnings or create payables in this step.

## Why Payroll and Earnings Are Deferred

Teacher earnings affect Teacher Salary Expense and Teacher Payables. The exact earning timing, package-course rules, attendance/cancellation treatment, deductions, and branch scope remain payroll workflow concerns and must be implemented in the payroll step with tests and accounting posting through the centralized accounting service.

## BS/AD Date Handling

Teacher records store AD dates for sorting and integrations and BS date strings for Nepali user-facing workflows. Full BS/AD conversion remains dependent on the approved Nepali calendar table or library.

## Constraints

This step does not implement class assignment, teacher earnings, teacher payments, payroll services, accounting posting, teacher APIs, frontend pages, attendance, or fixed salary generation.

## Status

Accepted.
