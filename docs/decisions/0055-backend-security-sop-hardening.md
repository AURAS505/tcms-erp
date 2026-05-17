# 0055 - Backend Security and SOP Hardening

## Status
Accepted

## Context
Before final UI polish and production readiness, the backend was reviewed against SOP-critical controls: backend permission enforcement, branch isolation, session/CSRF safety, financial immutability, maker-checker, audit logging, and dangerous mutation endpoints.

## Reviewed Areas
- Shared branch permissions and scoped querysets.
- Billing, payroll, accounting, and academic rollover mutation views.
- Financial service-layer posting, approval, reversal, and rollover behavior.
- Immutable posted/reversed/void financial models.
- CORS, session authentication, CSRF middleware, and trusted origins.
- Audit logging in sensitive financial services.
- Read-only report and journal visibility endpoints.

## Fixes Made
- Hardened accounting report endpoints so branch-scoped users cannot request organization-wide reports by omitting the branch filter.
- Branch-scoped report users with exactly one assigned branch are scoped to that branch automatically.
- Branch-scoped report users with no active branch assignment are denied.
- Branch-scoped report users cannot request an unassigned branch.
- Added `GET /api/v1/auth/csrf/` to issue a CSRF token and cookie for session-cookie frontend clients.
- Added tests for CSRF token issuance and branch-scoped report isolation.

## Confirmed Controls
- Financial mutation views delegate business behavior to service-layer methods.
- Approval/posting endpoints use backend role permissions; frontend hiding is not relied on for security.
- Maker-checker checks exist for student payments, billing adjustments/refunds, payroll approvals/posting, and manual journals.
- Posted journal entries, posted payments, posted payroll records, and executed rollover records remain immutable.
- Journal reversals create opposite entries rather than editing/deleting the original.
- Hard-closed academic years block accounting posting.
- Sensitive financial actions record audit logs through the service layer.

## Remaining Limitations
- Login and password reset rate limiting remain pending production hardening work.
- Full private-file handling and upload validation remain pending for future file workflows.
- CSRF frontend consumption should be wired in the frontend API client before production cookie-auth deployment.

This hardening pass aligns the backend with the current TCMS SOP requirement that authorization, branch isolation, financial immutability, and auditability are enforced server-side.
