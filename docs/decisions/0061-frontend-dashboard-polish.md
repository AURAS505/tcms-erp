# 0061 - Frontend Dashboard Polish

## Status

Accepted

## Context

Step 24D implements Stage 3 of the final UI polish plan. The previous dashboard was a static placeholder that confirmed the protected shell but did not yet feel like an ERP home screen.

The Volt dashboard reference was used only as visual inspiration for spacing, cards, and dashboard hierarchy. No Volt source code, repository import, Bootstrap dependency, or template code was used.

## Decision

The dashboard landing page now presents a TCMS ERP control center with:

- A stronger welcome header using the authenticated user's name where available.
- Session context for role, branch assignment count, and backend-enforced security.
- Role-aware module shortcut cards for students, classes, billing, payroll, accounting, and academic years.
- Safe summary cards that link to existing modules without inventing financial or operational totals.
- An operational checklist focused on branch context, maker-checker approval, BS/AD dates, and ledger source-of-truth behavior.
- Role-aware quick actions that use existing routes only.

## No Fake Metrics

No fake financial numbers, student counts, due totals, payable totals, or journal counts were added. Summary cards intentionally use neutral "View module" language until dedicated dashboard aggregation APIs exist.

## Role Behavior

- Receptionist-style roles can access student, class, and billing workspaces.
- Accountant-style roles can access billing, payroll, accounting, and finance-related quick actions.
- Teacher role is limited to class and academic-year workspaces.
- Auditor role receives read-oriented module access and no mutation quick actions.

Backend authorization remains authoritative. Frontend role filtering is a usability layer only.

## Future Opportunities

Future dashboard API work can add real aggregate endpoints for:

- Active students by branch and academic year.
- Open dues and receivable aging.
- Teacher payable aging.
- Pending approvals.
- Posted journal and trial balance health.

Those APIs should be backend-permissioned, branch-aware, and ledger-reconciled before replacing the current neutral cards.
