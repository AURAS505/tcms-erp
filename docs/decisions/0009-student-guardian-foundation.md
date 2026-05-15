# 0009 Student and Guardian Foundation

## Decision

Create student and guardian data foundations before enrollment, billing, payments, teacher workflows, and frontend screens.

## Student Admission Foundation

The student module now stores inquiries, admission profiles, documents, academic records, school history, status history, and notes. These records capture the admission SOP without implementing approval APIs or enrollment services yet.

## Student Status Lifecycle

Students support the lifecycle statuses required by the SOP: inquiry, pending, active, on break, left, graduated, and rejected. The model exposes a simple `can_be_enrolled` helper that returns true only for active students. Actual enrollment rules are intentionally deferred to the classes/enrollment step.

## Guardian and Family Structure

The guardian module stores family records, guardian profiles, and student-guardian links. This supports primary contacts, notification/payment/refund permission flags, and future guardian portal features while keeping guardian records branch-scoped.

## Why Enrollment and Billing Are Deferred

Admission data must exist before enrollment and fee workflows, but enrollment creates contractual class relationships and billing creates receivables. Those require class, billing, and accounting services that are not part of this step.

## BS/AD Date Handling

Student records store AD dates for sorting and consistency and BS date strings where user-facing Nepali date behavior is required. Full BS/AD conversion remains dependent on the approved calendar source.

## Constraints

This step does not implement class enrollment, fee dues, payments, accounting posting, admission APIs, approval APIs, frontend pages, file storage services, teacher modules, or school directory modules.

## Status

Accepted.
