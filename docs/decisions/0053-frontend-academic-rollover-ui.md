# 0053 Frontend Academic Rollover UI

## Status
Accepted

## Context
Academic rollover APIs expose service-backed workflows for prepare, validate, execute, cancel, summary, soft close, and hard close. Operators need a compact UI to run these actions without moving rollover accounting rules into the browser.

## Decision
Add frontend pages for academic years and academic rollovers:

- `/dashboard/academic-years`
- `/dashboard/academic-years/[id]`
- `/dashboard/academic-rollovers`
- `/dashboard/academic-rollovers/[id]`
- `/dashboard/academic-rollovers/new`

The UI supports preparing rollovers, validating readiness, executing with new-year data, cancelling pending rollovers, viewing summary state, and soft/hard closing academic years.

## Backend Source Of Truth
The frontend does not calculate closing entries, opening entries, retained earnings movements, or trial balance state. It submits operator intent to secured backend endpoints. Backend services remain responsible for validation, posting, audit logging, hard-close protection, and rollover accounting.

## Role Gating
Super Admin, Institute Owner, and Accountant roles can see rollover workflow actions. Hard close is visible only to Super Admin and Institute Owner. Receptionist, Teacher, and Auditor users see read-only pages.

## High-Risk Warnings
Rollover and year close actions are labeled as high-risk financial workflows. Execute screens warn that backend validation and posting will occur.

## Remaining Limitations
The UI does not show generated closing/opening journal previews, does not implement bank reconciliation or tax filing, and does not create academic periods for the new year.

## Volt Reference
The Volt dashboard prompt remains reference-only for visual direction. No Volt source code is copied.
