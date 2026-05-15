# ADR 0018: Backend API Foundation

## Status
Accepted

## Context
TCMS ERP needs a consistent Django REST Framework API foundation before frontend work. The backend already has service-layer financial workflows, but workflow mutation endpoints must not be exposed casually.

## Decision
1. Add `/api/v1/` as the stable API prefix.
2. Keep `/api/health/` unchanged.
3. Add per-app `serializers.py`, `views.py`, and `urls.py` modules for foundational resources.
4. Use DRF `ModelSerializer` and shared base viewsets from `common.viewsets`.
5. Require authentication by default through DRF settings.
6. Add placeholder role/branch-aware permissions in `common.permissions`.
7. Use standard pagination from `common.pagination`.
8. Expose operational CRUD endpoints for foundational non-financial modules.
9. Expose financial records as read-only endpoints for now.
10. Expose read-only accounting report endpoints for:
    - trial balance
    - general ledger
    - profit and loss
    - balance sheet

## Financial Endpoint Policy
Billing, payroll, accounting, rollover, and posting workflows remain service-layer only in this step. Posted financial records are not writable through APIs. Payment approval, teacher payment posting, journal posting, and rollover execution APIs will be introduced later with explicit service-backed tests.

## Security
All viewsets use authenticated access by default. Branch scoping is implemented as a placeholder using user branch assignments where available, with superusers allowed globally. Full login/session/password-reset APIs are intentionally left for the next auth-focused step.

## Not Implemented In This Step
- Login/logout/password reset APIs.
- Frontend pages.
- Payment approval APIs.
- Manual journal posting APIs.
- Academic rollover execution APIs.
- PDF/Excel exports.
