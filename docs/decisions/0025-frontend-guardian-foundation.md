# ADR 0025: Frontend Guardian Foundation

## Status
Accepted

## Context
The student read-only frontend foundation is in place. The next operational slice is guardian and family visibility using existing backend endpoints under `/api/v1/families/`, `/api/v1/guardians/`, and `/api/v1/student-guardians/`.

## Decision
1. Add read-only list and detail pages for guardians and families.
2. Add compact guardian/family frontend types and API client helpers.
3. Add sidebar navigation entries for `Guardians` and `Families`.
4. Keep student detail read-only and add a guardian relationship placeholder.
5. Do not add guardian, family, or student-guardian write/linking workflows in this step.
6. Keep Volt React Dashboard reference-only for general admin spacing and table/card feel. No Volt source code, component names, sample data, Bootstrap dependency, or template structure is copied.

## Student Detail Context
The backend has a `student-guardians` endpoint, but the current shared filtering mixin does not expose direct `student` filtering. Student detail therefore shows a clean placeholder until relationship filtering is available.

## Pending
Guardian create/edit, family create/edit, student-guardian linking, direct relationship filtering, guardian cards inside student detail, class/enrollment, billing, payment, payroll, accounting, charts, and reports remain pending.

## Consequences
The frontend now has read-only family and guardian surfaces that match the student module pattern and can be extended once linking workflows are ready.

