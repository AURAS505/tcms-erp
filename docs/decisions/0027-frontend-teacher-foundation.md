# ADR 0027: Frontend Teacher Foundation

## Status
Accepted

## Context
Student, guardian, family, class, subject, and enrollment read-only frontend foundations are in place. The next operational slice is teacher visibility using existing backend endpoints for teachers, teacher contracts, teacher activities, and teacher status history.

## Decision
1. Add read-only list and detail pages for teachers and teacher contracts.
2. Add compact frontend types and API helpers for teachers, contracts, activities, and status history.
3. Add sidebar navigation entries for `Teachers` and `Teacher Contracts`.
4. Keep teacher detail read-only with a placeholder for filtered contracts, activities, and status history.
5. Do not add teacher create/edit, contract create/edit, payroll, payment, billing, or accounting UI in this step.
6. Keep Volt React Dashboard reference-only for general admin spacing, cards, and table feel. No Volt source code, component names, sample data, Bootstrap dependency, or template structure is copied.

## Payroll Boundary
Teacher contracts can affect payroll calculations, but payroll earning generation and teacher payment workflows are intentionally excluded. Those flows need maker-checker, accounting posting, payment allocation, and audit rules handled in their own frontend slice.

## Pending
Teacher create/edit, teacher contract create/edit, filtered teacher contracts, filtered teacher activity, status history sections, payroll, teacher payment, billing, accounting, charts, reports, and approval workflows remain pending.

## Consequences
The frontend now has a teacher module foundation that can support future class and payroll workflows without introducing finance behavior early.
