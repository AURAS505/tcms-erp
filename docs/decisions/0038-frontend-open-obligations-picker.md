# 0038 Frontend Open Obligations Picker

## Status
Accepted

## Context
The payment allocation picker previously loaded read-only dues and invoices with broad organization/branch/year filters, then filtered the current page of results by student in the browser. That was not reliable with pagination and duplicated part of the backend's branch-scope responsibility.

## Decision
Update the frontend payment allocation picker to call backend-filtered open obligation queries after a student is selected:

- `GET /api/v1/student-fee-dues/?student=<id>&open_only=true`
- `GET /api/v1/student-invoices/?student=<id>&open_only=true`

The frontend may also pass organization, branch, and academic year filters when selected in the payment form. The picker keeps local search, but only within the backend-filtered open results.

## Behavior
The picker shows due or invoice reference, due date where available, status, and visible balance. Advance payments continue to hide allocation controls. The frontend blocks allocation amounts greater than the selected visible balance as a usability guard.

## Source of Truth
The backend remains authoritative for branch scope, open-obligation filtering, allocation validation, payment posting, receipt assignment, and accounting side effects. The frontend no longer relies on client-side filtering over a partial paginated obligation list.

## Pending
This remains a single-allocation UI. Multi-item allocation, automatic allocation, and other financial workflows such as discounts, waivers, fines, refunds, payroll, and accounting journals are not included.
