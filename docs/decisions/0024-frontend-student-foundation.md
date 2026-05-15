# ADR 0024: Frontend Student Foundation

## Status
Accepted

## Context
The authenticated dashboard shell is ready, so TCMS ERP can add its first operational frontend slice. The backend already exposes `/api/v1/student-inquiries/` and `/api/v1/students/` through DRF viewsets.

## Decision
1. Add read-only list and detail pages for students and student inquiries.
2. Use existing backend API endpoints only; no create, edit, conversion, or approval mutations are implemented.
3. Add compact reusable operational UI components for headers, tables, status badges, loading, empty, and error states.
4. Add student-specific frontend types and API client helpers.
5. Add sidebar navigation entries for `Students` and `Student Inquiries`.
6. Keep Volt React Dashboard reference-only for general admin spacing and card/table feel. No Volt source code, component names, sample data, Bootstrap dependency, or template structure is copied.

## Pending
Student create/edit forms, inquiry conversion, admission approval, guardian pages, documents workflow, class enrollment, billing, payments, payroll, accounting, charts, and reports remain pending.

## Consequences
The frontend now has a small operational pattern that future TCMS modules can reuse without introducing finance or write workflows prematurely.

