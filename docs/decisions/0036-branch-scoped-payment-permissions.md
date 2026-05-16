# 0036 Branch-Scoped Payment Permissions

## Status
Accepted

## Context
Student payment workflow APIs were protected by role permissions and service-layer maker-checker rules. Branch-scoped users still needed stricter backend enforcement so a user assigned to one branch could not create, approve, void, list, or retrieve payments from another branch.

## Decision
Harden branch-scope checks for student payment APIs.

The backend now provides shared helpers to:

- read active branch assignments for a user;
- check whether a user can access a specific branch;
- allow Super Admin and Institute Owner users to bypass branch restrictions;
- deny branch-scoped access when a branch-scoped user has no active branch assignment.

Student payment actions use these rules as follows:

- `create-draft` verifies the requested branch is accessible before calling `StudentPaymentService`.
- `approve` resolves the payment through the scoped queryset before calling the service.
- `void-placeholder` resolves the payment through the scoped queryset before calling the service.
- list and retrieve responses are filtered to assigned branches for branch-scoped users.

## Role Behavior
Branch Admins, Accountants, Receptionists, Auditors, and Teachers are branch-scoped. Branch-scoped users with no active branch assignment receive no branch records by default.

Super Admin and Institute Owner users retain all-branch access. Financial approval roles and maker-checker rules still apply independently, so branch access alone does not grant approval authority.

Auditors remain read-only. Teachers cannot mutate payment workflows.

## Service Layer
Payment creation, approval, posting, receipt assignment, due updates, immutability, and accounting entries remain in the service layer. The viewset only enforces API access boundaries before service methods are called.

## Pending
This decision focuses on student payment APIs. The same deny-by-default branch-scope pattern should be reviewed across other operational and financial modules before mutation workflows are expanded.
