# 0051 Frontend Accounting Document Reference UI

## Status
Accepted

## Context
Journal mutation APIs support attaching simple accounting document references to journal entries. The frontend needs a compact operator workflow without introducing file upload behavior.

## Decision
Add a metadata-only "Add Document Reference" form to journal entry detail pages.

The form captures document type, reference number, and description, then calls `POST /api/v1/journal-entries/{id}/documents/` through the existing `attachAccountingDocument()` helper.

## File Upload
Real file upload is intentionally pending. The UI does not expose a file input, does not upload binaries, and does not attempt to manage storage paths.

## Role Gating
The document reference action is visible only to Super Admin, Institute Owner, and Accountant roles. Receptionist, Teacher, and Auditor users retain read-only access and do not see the action.

## Backend Source Of Truth
The backend remains responsible for permission checks, branch scope, validation, audit logging, and persistence. The frontend only submits metadata.

## Volt Reference
The Volt dashboard prompt remains reference-only for visual direction. No Volt source code is copied.
