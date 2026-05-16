# 0032 Student Payment Workflow APIs

## Status
Accepted

## Context
The backend already has `StudentPaymentService` for draft payment creation, allocation validation, maker-checker approval, receipt assignment, due/invoice balance updates, advance balance updates, and accounting journal posting. The frontend now needs safe mutation endpoints for the student payment workflow without exposing direct model writes.

## Decision
Expose service-backed actions on the existing student payment API:

- `POST /api/v1/student-payments/create-draft/`
- `POST /api/v1/student-payments/{id}/approve/`
- `POST /api/v1/student-payments/{id}/void-placeholder/`

The API serializers only validate request shape and resolve related records. They do not duplicate payment business rules. Draft creation and approval/posting are delegated to `StudentPaymentService`.

## Draft Payment Behavior
Draft creation accepts organization, branch, academic year, student, payment date, method, amount, optional reference fields, optional allocation targets, and advance-payment flag.

Draft payments:

- receive a draft receipt number only;
- do not create journal entries;
- do not update dues, invoices, advance balances, or the general ledger;
- use service-layer allocation validation.

## Approval and Posting Behavior
Approval calls `StudentPaymentService.approve_payment()`, which posts the payment as the financial event.

Posted payments:

- enforce maker-checker rules;
- assign the official receipt number during posting;
- update dues, invoices, or advance balances through the service;
- create balanced journal entries through `AccountingPostingService`;
- remain immutable through existing model protections.

## Permissions
The endpoints require authenticated access through the existing API permission foundation. The service enforces maker-checker. Dedicated role gating for accountant, institute owner, and super-admin approval remains a pending hardening step once role assignment workflows are fully wired into operational UI and tests.

## Not Included
This decision does not expose mutation APIs for discounts, waivers, fines, refunds, payroll, manual journal posting, reversals, bank reconciliation, or academic year rollover. It also does not add frontend payment screens.

## Follow-Up
Frontend payment creation and approval screens can now call the service-backed endpoints. The next backend hardening step should add explicit financial role permissions for approval/posting actions.
