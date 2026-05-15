# 0005 Organizations Module Foundation

## Decision

Create the organizations foundation before business modules so TCMS ERP has a stable organization and branch scope for future data isolation, settings, taxes, and approval workflows.

## Scope

Step 4 adds:

- `Organization`
- `Branch`
- `OrganizationSetting`
- `TaxRate`
- `ApprovalRule`
- Django admin registrations
- Initial model tests
- Initial organizations migration

## Organization and Branch Design

`Organization` represents the legal education business or institute group. It stores legal identity, contact details, registration/tax identifiers, default currency, and an optional logo placeholder.

`Branch` belongs to an organization and stores branch code, name, contact details, active status, and main-branch marker. Branches are introduced before student, billing, payroll, and accounting modules because those modules must later enforce branch-scoped access and reporting.

## Future Branch-Level Isolation

Branch-level data isolation is mandatory for Branch Admins and Receptionists, while Super Admin and Institute Owner can access all branches. Future domain models should carry `organization_id` and `branch_id` foreign keys where branch scope applies. Backend permissions must enforce that scope; frontend hiding is not security.

## Approval Rule Foundation

`ApprovalRule` stores the organization, optional branch, module, action, amount range, required role, and escalation role needed by future maker-checker workflows. This step does not implement approval services or enforcement. It only records the configuration shape that later financial workflows can use.

## Tax Setting Placeholder

`TaxRate` stores organization-specific tax names, types, percentages, active state, and effective date ranges. Tax calculation and posting are not implemented because tax policy remains a clarification item.

## Constraints

This step does not implement student, teacher, class, billing, payroll, accounting, login APIs, frontend pages, academic year logic, maker-checker enforcement, or financial posting logic.

## Status

Accepted.
