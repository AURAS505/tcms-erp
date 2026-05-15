# Development Roadmap

This roadmap follows the required implementation order. Each step must be handled as a reviewable ticket-sized change.

## Step 0: Repository and Document Analysis

Analyze available documents, SOPs, README files, old code, and requirements. No production code.

Status: complete for current workspace. No prior documents were found.

## Step 1: Monorepo Foundation

Create monorepo foundation, Docker, backend skeleton, frontend skeleton, README, `.env.example`, and initial docs.

Status: complete.

## Step 1.5: Sync Master Requirements Into Repository

Persist master requirements into repository documentation so future implementation does not depend only on chat history.

Status: complete when this document and related requirement files are committed.

## Step 2: Backend Common Utilities

Build:

- UUID base model
- Timestamp model
- Soft delete where appropriate
- Audit mixin
- Money field utilities
- Nepali date utilities placeholder
- Common exceptions
- Permission base classes
- Pagination
- API response helpers

## Step 3: Accounts Module

Build:

- Custom user foundation
- Roles and permissions
- Branch assignment
- Auth foundation
- Password reset foundation
- Maker-checker helper primitives

## Step 4: Organizations Module

Build:

- Organizations
- Branches
- Organization settings
- Approval matrix
- Tax settings placeholders

## Step 5: Academic Module

Build:

- Academic years
- Academic periods
- Nepali date mapping
- One-active-year enforcement
- Period close states

## Step 6: Accounting Foundation

Build:

- Chart of accounts
- Accounting periods
- Journal entries
- Journal lines
- Posting service
- Balance validation

No unclear financial logic should be implemented without clarification.

## Step 7: Audit Logging and Immutability

Build:

- Audit logging service
- Immutable financial record controls
- Reversal prerequisites

## Step 8: Student and Guardian Modules

Build:

- Student inquiry
- Admission workflow
- Student profile
- Documents
- Guardian linking
- Status workflow

## Step 9: Teacher Module

Build:

- Teacher profile
- Contracts
- Earning model configuration

## Step 10: Classes Module

Build:

- Classes
- Batches
- Sections
- Subjects
- Enrollments
- Breaks
- Withdrawals

## Step 11: Billing Foundation

Build:

- Fee plans
- Dues
- Invoices
- Invoice items

## Step 12: Student Payment Workflow

Build:

- Draft payments
- Approval
- Receipt sequence
- Allocation
- Cash and bank posting

## Step 13: Adjustments and Refunds

Build:

- Advance payments
- Discounts
- Waivers
- Fines
- Refund workflows

## Step 14: Payroll

Build:

- Teacher earnings
- Payment batches
- Teacher payments
- Allocations

## Step 15: Financial Reports

Build:

- General ledger
- Trial balance
- Profit and loss
- Balance sheet
- Cash flow

## Step 16: Academic Year Rollover

Build:

- Validation
- Closing entries
- Opening entries
- New year creation
- Hard close

## Step 17: Frontend Foundation

Build:

- Dashboard layout
- Authentication pages
- Role-based navigation

## Step 18: Frontend Operational Modules

Build:

- Students
- Guardians
- Teachers
- Classes
- Enrollments

## Step 19: Frontend Finance Modules

Build:

- Billing
- Payroll
- Accounting workflows

## Step 20: Reports and Settings

Build:

- Reports
- Exports
- Audit viewer
- Settings

## Step 21: Testing Hardening

Build:

- Backend unit and integration tests
- Frontend tests
- E2E critical flows

## Step 22: DevOps Production Readiness

Build:

- CI/CD hardening
- Backup scripts and SOPs
- Staging deployment docs
- Monitoring docs

## Step 23: Final QA and Release Checklist

Build:

- Final QA plan
- Documentation review
- Release checklist
- Deployment signoff process
