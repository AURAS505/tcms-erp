# 0011 Classes Module Foundation

## Decision

Create class, subject, schedule, enrollment, break, discount, withdrawal, and teacher transfer foundations before billing, payroll, accounting posting, APIs, and frontend screens.

## Class and Subject Design

Subjects are organization-scoped reference records with optional branch and academic year scope. They are informational in this step and do not trigger fee generation.

Class rooms represent the operational class, batch, and section. They are scoped to organization, branch, and academic year, and can reference a primary teacher and multiple subjects. The unique class/batch/section constraint protects the SOP rule that the same class offering should not be duplicated inside the same branch and academic year.

## Enrollment Design

Class enrollment stores the contractual relationship between an active student and a class room. It captures joined dates, lifecycle status, enrollment-level discount placeholders, and teacher cut override placeholders. A database constraint prevents duplicate active/on-break enrollment for the same student and class.

Model validation checks branch, organization, and academic year alignment. No API workflow is implemented yet.

## Break, Discount, Withdrawal, and Teacher Transfer Placeholders

Enrollment breaks represent approved or pending interruptions that future billing services will use to pause due generation.

Enrollment discounts represent scholarship, sibling, merit, hardship, and other discount decisions. Approval fields are present, but maker-checker enforcement and accounting treatment are deferred.

Student withdrawals record the operational withdrawal review. Future billing logic will settle open dues, cancel future dues, and handle advances/refunds.

Teacher transfers record class teacher changes. They do not create teacher earnings or payroll records in this step.

## Why Billing, Dues, and Teacher Earnings Are Deferred

Billing due generation affects receivables and revenue. Teacher earnings affect Teacher Salary Expense and Teacher Payables. Both require reviewed financial policies, maker-checker workflows, and centralized accounting posting services, so this step only stores operational configuration and lifecycle data.

## BS/AD Date Handling

Classes, schedules, enrollments, breaks, discounts, withdrawals, and transfers store AD dates for sorting and integrations and BS date strings for Nepali user-facing workflows. Full conversion remains dependent on the approved Nepali calendar source.

## Constraints

This step does not implement fee due generation, student payments, teacher earnings, payroll, accounting posting, class/enrollment APIs, frontend pages, attendance, exams, or notification workflows.

## Status

Accepted.
