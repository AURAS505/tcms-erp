# 0045 Frontend Payroll Mutation UI

## Status
Accepted

## Context
Step 21F added secured backend payroll mutation APIs for teacher earnings and teacher payments. Payroll users now need frontend workflows for creating manual earnings, approving/posting earnings, creating draft teacher payments, and approving/posting teacher payments.

## Decision
Add payroll-only mutation UI:

- `/dashboard/payroll/earnings/new` creates manual teacher earnings.
- Teacher earning detail shows approve/post actions when status and role allow it.
- `/dashboard/payroll/payments/new` creates draft teacher payments.
- Teacher payment detail shows approve/post actions when status and role allow it.

The frontend calls only the Step 21F payroll workflow endpoints. It does not calculate accounting effects, create journal entries, or mutate posted records directly.

## Role Gating
Payroll mutation actions are visible only to:

- Super Admin
- Institute Owner
- Accountant

Receptionist, Teacher, and Auditor users can continue viewing payroll records where backend branch permissions allow, but they do not see payroll mutation actions.

## Backend Source Of Truth
The backend remains responsible for branch access, maker-checker enforcement, record state validation, allocation validation, immutability, and accounting posting. The frontend submits user intent and displays the resulting backend state.

## Manual Allocation Limitation
The first teacher payment draft UI supports one manual allocation row using a teacher earning ID plus allocation amount. This keeps the frontend small while relying on backend validation for branch, teacher, status, and balance checks. A later step can replace this with searchable posted-earning allocation pickers.

## Volt Reference
The Volt dashboard prompt remains reference-only for visual direction. No Volt source code is copied.

## Out Of Scope
Accounting journal mutation UI, academic rollover UI, automatic salary generation, attendance-based payroll calculation, and teacher payroll formula engines remain outside this step.
