# 0004 Accounts Module Foundation

## Decision

Create the custom accounts foundation before domain modules are implemented.

## Scope

Step 3 adds:

- Custom `User` model with UUID primary key
- Email login readiness with optional username
- Role and permission models
- User-role and role-permission assignment models
- Branch assignment placeholder using UUID organization and branch identifiers
- Password reset token model with hashed token storage
- Login session placeholder with hashed session key storage
- Django admin registrations
- Initial model tests

## Why Custom User Is Created Early

Django recommends defining a custom user model at project start. Changing `AUTH_USER_MODEL` after migrations and foreign keys exist is disruptive. TCMS ERP requires UUID identifiers, email login readiness, account status fields, force-password-change support, audit compatibility, and future branch-scoped access control, so the custom user model belongs in the foundation.

## Role and Permission Strategy

The accounts module stores TCMS-specific roles and permissions rather than relying only on Django's built-in permission tables. This gives the backend a stable authorization model for enterprise roles such as Super Admin, Institute Owner, Branch Admin, Accountant, Receptionist, Teacher, Auditor, Future Student Portal User, and Future Parent Portal User.

Frontend navigation may use these permissions later, but backend enforcement remains mandatory.

## Branch Assignment Placeholder

`UserBranchAssignment` stores `organization_id` and `branch_id` as UUID values until the organizations module creates formal organization and branch tables. This preserves the access-control shape without introducing cross-module dependencies before Step 4.

## Future Maker-Checker Compatibility

Financial maker-checker approval is not implemented in this step. The accounts foundation supports it later by providing stable user identifiers and assignment models that can distinguish transaction creators, approvers, and branch scope. Future financial models should reference `settings.AUTH_USER_MODEL` for creator and approver fields.

## Constraints

This step does not implement login APIs, session endpoints, JWT, frontend auth UI, organizations, accounting, billing, payroll, students, teachers, classes, or financial approval logic.

## Status

Accepted.
