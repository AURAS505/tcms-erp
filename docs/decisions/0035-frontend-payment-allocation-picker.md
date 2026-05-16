# 0035 Frontend Payment Allocation Picker

## Status
Accepted

## Context
The first student payment workflow UI allowed operators to type a due ID manually when creating a draft payment. That was service-backed and safe, but it was easy to mistype and did not show the visible balance before submitting.

## Decision
Replace the manual due ID field with a compact due/invoice allocation picker on the new student payment page.

The picker:

- loads existing read-only fee dues and invoices;
- filters the loaded results to the selected student;
- shows only open items with a positive visible balance;
- supports selecting one due or one invoice for this first UI slice;
- requires a positive allocation amount when a target is selected;
- blocks allocation amounts greater than the visible selected balance before submit;
- hides allocation controls for advance payments.

The submitted payload still uses the existing student payment draft API. Due selections send `fee_due`; invoice selections send `invoice`. Approval/posting APIs are unchanged.

## Backend Source of Truth
Frontend validation is a usability safeguard only. The backend student payment service remains authoritative for allocation validation, posting effects, due balance updates, receipt assignment, and accounting entries.

## Current Limitation
The frontend can pass organization, branch, and academic year query parameters to the read-only dues/invoices APIs. A dedicated student query parameter is not part of the current frontend contract, so the page filters the loaded result page by selected student. A backend-supported student filter should be added before this UI is used with large due/invoice volumes.

## Out of Scope
This step does not add discount, waiver, fine, refund, payroll, accounting journal, rollover, or posting mutation UI. It also does not add multi-due allocation or automatic allocation logic.

## Design
The UI remains Volt-inspired only: compact admin spacing, light cards, and restrained form controls. No Volt source code, component names, exact sample data, or template structure were copied.
