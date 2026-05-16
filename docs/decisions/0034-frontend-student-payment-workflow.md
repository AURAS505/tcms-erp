# 0034 Frontend Student Payment Workflow

## Status
Accepted

## Context
The backend now exposes secured, service-backed student payment workflow APIs for draft creation and approval/posting. The frontend needs a focused payment workflow UI without expanding into other financial mutation areas.

## Decision
Add a student payment draft page and payment detail approval action.

The frontend calls:

- `POST /api/v1/student-payments/create-draft/` for draft payments.
- `POST /api/v1/student-payments/{id}/approve/` for approval/posting.

The frontend does not calculate final accounting effects, receipt numbers, allocation side effects, due balances, or journal entries. The backend service remains the source of truth.

## Role Visibility
The payments list shows `New Payment` only for:

- Super Admin
- Institute Owner
- Branch Admin
- Accountant
- Receptionist

The payment detail page shows `Approve and post` only for:

- Super Admin
- Institute Owner
- Accountant

Receptionists can create draft payments but cannot approve. Teachers and auditors do not see payment mutation actions. Backend permissions remain authoritative even when frontend actions are hidden.

## Scope
This step supports a compact draft form with optional due ID allocation. Posted, voided, and refunded payments are shown as read-only.

## Pending
Future work should replace manual due ID allocation with searchable due/invoice allocation controls. Discount, waiver, fine, refund, payroll, accounting journal, reversal, export, and rollover mutation UIs are intentionally not included.

## Design
The UI remains Volt-inspired only: compact admin spacing, light cards, and restrained action buttons. No Volt source code, component names, or sample data were copied.
