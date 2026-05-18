# TCMS ERP RC-1 Release Notes

Date: 2026-05-18

## Release Candidate

TCMS ERP RC-1

Suggested tag:

```bash
git tag -a v0.1.0-rc1 -m "TCMS ERP v0.1.0 RC1"
git push origin v0.1.0-rc1
```

Do not create the tag until the release owner approves the release candidate.

## Summary

TCMS ERP RC-1 is the first release candidate for the modern full-stack education ERP. It includes the backend domain foundations, financial workflows, service-backed accounting controls, authenticated API layer, Next.js dashboard workflows, production Docker configuration, security hardening, dependency remediation, deployment documentation, and final UI polish verification.

The release candidate is ready for stakeholder review, staging validation with production-like secrets/domains, and manual release tag creation.

## Backend Modules Completed

- Accounts, roles, permissions, user branch assignments, authentication APIs, password reset, and forced password change.
- Organizations, branches, organization settings, tax placeholders, and approval rule foundation.
- Academic years, academic periods, Nepali calendar placeholders, and academic year rollover workflow.
- Students, guardians, families, admissions foundation, documents, history, and notes.
- Teachers, contracts, activities, and teacher status history.
- Classes, subjects, schedules, enrollments, breaks, discounts, withdrawals, and teacher transfer placeholders.
- Billing data foundation, student payment workflow, advance application, discounts, waivers, fines, and advance refund workflow.
- Payroll foundation, teacher earning recognition, teacher payment workflow, deductions, payment batches, and allocations.
- Accounting foundation, chart of accounts, journal entries, posting service, financial reports, audit logging, and immutable financial record controls.
- Health, deep health, backup, restore, and deployment support utilities.

## Frontend Modules Completed

- Next.js TypeScript authenticated dashboard shell.
- Login, logout, current user, password reset, and forced password change flows.
- Dashboard landing page with module shortcuts and safe operational guidance.
- Students, guardians, teachers, classes, academic years, rollovers, billing, payroll, accounting, reports, audit, settings, and operational workflow pages for current release scope.
- Shared UI primitives for buttons, inputs, tables, status badges, page headers, detail cards, form cards, warning panels, empty states, loading states, and error states.
- Volt-inspired visual direction implemented with original TCMS code and no copied Volt source.
- Responsive and accessibility polish for representative operational and financial pages.

## Financial And Accounting Controls Completed

- Double-entry journal model and posting validation.
- Posted journal immutability and reversal-oriented correction principle.
- Maker-checker enforcement for implemented financial workflows.
- Student payment posting:
  - cash/bank debit
  - student receivable credit
  - advance liability handling
- Advance application:
  - student advance revenue debit
  - student receivable credit
- Discounts, waivers, fines, and advance refunds with corresponding ledger entries.
- Teacher earning recognition:
  - teacher salary expense debit
  - teacher payable credit
- Teacher payment posting:
  - teacher payable debit
  - cash/bank credit
- General ledger, trial balance, profit and loss, balance sheet, cash flow foundation, and reconciliation report services.
- Academic year rollover validation, revenue/expense closing, opening balance posting, and active-year controls.
- Central audit log foundation for financial and security-sensitive workflows.

## Security Controls Completed

- Backend-enforced API permissions and branch-scope foundations.
- Session/cookie-ready authentication APIs.
- Password reset tokens stored hashed, not raw.
- Generic password reset request responses.
- CSRF, CORS, cookie, and production security documentation.
- Auth rate-limiting readiness documented for deployment configuration.
- Private file validation and storage guidance.
- Audit logging for sensitive workflows.
- Posted financial record immutability controls.
- npm audit clean after dependency remediation.

## Deployment Readiness Completed

- Local Docker Compose setup.
- Production Compose template.
- Production backend and frontend Dockerfiles.
- PostgreSQL, Redis, Celery worker, and Celery beat configuration.
- Production image build and smoke test completed.
- Health and deep health endpoints verified.
- Backup and restore scripts and SOPs.
- Monitoring and logging documentation.
- Go-live runbook.
- Rollback SOP.
- Production release checklist.
- Final release verification report.
- Final UI polish verification report.

## Known Limitations

- `next lint` shows a deprecation warning and should be migrated to the ESLint CLI before a future Next.js 16 upgrade.
- DRF Decimal serializer warnings remain as non-blocking cleanup items.
- Actual production secrets, domains, CORS origins, CSRF origins, and TLS certificates are not configured in the repository.
- Remote encrypted backup scheduling is documented but not configured with real production destinations.
- Formal RTO/RPO values are not finalized.
- Optional Sentry SDK wiring is not completed.
- Real production data migration is not included in RC-1.
- Real private file serving and signed URL delivery remain pending.
- Full bank reconciliation UI is not included in RC-1.
- Dashboard aggregate metrics intentionally remain limited until real aggregate APIs are introduced.
- Browser-based screenshot regression tooling is not configured.

## Not Included In RC-1

- Public SaaS tenant onboarding and billing.
- OAuth/social login and 2FA.
- Full bank reconciliation workflow UI.
- Full notification delivery workflows.
- Advanced charting and executive analytics.
- Exam management, attendance management, and LMS features.
- Production email/SMS provider integration with real credentials.
- Production infrastructure provisioning scripts for a specific cloud vendor.
- Migration of real legacy TCMS data.

## Manual QA Checklist

- Confirm release commit and tag candidate.
- Confirm no `.env` files, local databases, cache folders, `node_modules`, `.next`, or local reference source folders are staged.
- Run backend checks:
  - `python manage.py check`
  - `python manage.py makemigrations --check`
  - `python manage.py migrate`
  - `python -m pytest`
  - `python -m ruff check .`
- Run frontend checks:
  - `cd apps/frontend`
  - `npm audit`
  - `npm run lint`
  - `npm run typecheck`
  - `npm run test`
  - `npm run build`
- Run Docker checks:
  - `docker compose config --quiet`
  - `docker compose -f docker-compose.yml -f docker-compose.prod.yml config --quiet`
  - `docker compose -f docker-compose.yml -f docker-compose.prod.yml build backend frontend`
- Smoke test:
  - frontend loads
  - login page loads
  - backend `/api/health/` returns healthy
  - backend `/api/health/deep/` returns healthy
  - admin route responds
  - Celery worker and beat start
  - PostgreSQL and Redis are healthy
- Verify representative pages:
  - dashboard
  - students
  - billing payments
  - payroll payments
  - accounting journal entries
  - reports
  - academic rollovers
  - audit logs
- Confirm finance controls:
  - posted records are read-only
  - maker-checker blocks self-approval
  - audit logs are created for financial postings
  - trial balance report remains balanced in test/staging data
- Confirm deployment documents:
  - production checklist
  - go-live runbook
  - rollback SOP
  - backup and restore SOP
  - monitoring and logging guide

## Tagging Instructions

After final approval, create and push the release candidate tag manually:

```bash
git tag -a v0.1.0-rc1 -m "TCMS ERP v0.1.0 RC1"
git push origin v0.1.0-rc1
```

Verify the pushed tag:

```bash
git ls-remote --tags origin v0.1.0-rc1
```

## Release Readiness Status

RC-1 is documentation-ready and implementation-ready for manual release tagging. Remaining work is operational: final stakeholder approval, staging deployment with real environment values, production secret/domain configuration, and manual tag creation.
