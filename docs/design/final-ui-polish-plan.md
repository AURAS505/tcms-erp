# Final UI/UX Polish Plan

Date: 2026-05-18

## Scope

This plan defines the final frontend polish pass for TCMS ERP. It uses `docs/volt-dashboard-master-prompt.md` as visual inspiration only. No Volt source code, repository imports, Bootstrap dependency migration, or copied components should be used.

The polish pass must preserve the existing backend-authoritative workflows, financial controls, permission boundaries, CSRF behavior, and accounting logic.

## Current UI Status

The frontend already has a working Next.js dashboard foundation:

- Protected app shell with sidebar, topbar, and dashboard content area.
- Volt-inspired core palette: dark navy sidebar, indigo primary action color, light blue-gray body background, white cards, and soft card shadows.
- Reusable UI primitives: `Button`, `TextInput`, `SearchInput`, `PageHeader`, `SimpleTable`, `StatusBadge`, `MoneyDisplay`, `EmptyState`, `LoadingState`, and `ErrorState`.
- List/detail/new pages for core operational and financial modules.
- Service-backed financial action pages for billing payments, payroll payments, journal entries, and academic rollovers.

The current UI is functionally complete enough for workflow verification, but it still reads as a foundation rather than a finished enterprise dashboard.

## Visual Gaps

- Styling values are repeated inline across pages instead of flowing through shared design tokens.
- Cards, buttons, inputs, tables, and status states are close to the intended direction but need a tighter shared rhythm.
- Many pages use plain text-heavy descriptions that are useful during development but should be reduced before release.
- Dashboard landing content is still placeholder-oriented and does not yet provide a confident operational overview.
- Tables are readable, but list pages need consistent toolbar, filter, count, and pagination treatment.
- Detail pages use repeated local `DetailItem` functions instead of a common description-list pattern.
- Forms work but are visually dense and need clearer grouping, sticky totals/action areas where useful, and stronger validation hierarchy.
- Icons are not yet used in the sidebar/topbar/buttons, even though the intended direction expects familiar dashboard symbols.

## Layout Issues

- `AppShell` uses a fixed large-screen sidebar but no mobile drawer or collapsed navigation state.
- Main content padding is serviceable but should be standardized with responsive max widths for dense workflows.
- `PageHeader` action groups can become cramped on small screens and should wrap predictably with full-width controls where needed.
- Detail pages use grids effectively, but side panels vary in purpose and tone across modules.
- Form pages sometimes place high-risk financial warnings, allocation controls, and submit actions in the same visual weight.
- Empty/loading/error states occupy inconsistent visual height across list, detail, and form screens.

## Sidebar And Topbar Improvements

Target direction:

- Keep the dark navy sidebar, fixed desktop layout, and light topbar.
- Add module grouping: Overview, Academic, People, Classes, Billing, Payroll, Accounting, Reports, Administration.
- Add simple icons to navigation items using the existing frontend dependency set if available; otherwise defer icon work rather than adding a large dependency.
- Improve active state with a clearer indigo pill, consistent text contrast, and a subtle left accent.
- Add a compact user/branch context block that shows role and branch without exposing security-sensitive assumptions.
- Add mobile behavior: hamburger button, overlay drawer, close button, and keyboard/escape handling.
- Add topbar breadcrumbs from current route segments.
- Add topbar search placeholder only if it can route to a real global search later; otherwise avoid decorative inactive search.
- Keep logout visible and avoid hiding security actions in a fragile custom dropdown.

## Dashboard Page Improvements

Replace placeholder cards with a release-ready operational overview:

- Summary cards:
  - Active students.
  - Pending financial approvals.
  - Open receivables.
  - Teacher payables.
- Quick module shortcuts:
  - New student inquiry.
  - Create payment draft.
  - Review payment approvals.
  - Journal entries.
  - Trial balance.
  - Academic rollover.
- Recent activity sections:
  - Latest student payments.
  - Latest teacher payments.
  - Recent journal entries.
- Risk/status panels:
  - Open financial approvals.
  - Academic year status.
  - Deep health status if exposed safely.

Do not add charts unless the data is real and backend-backed. A polished enterprise dashboard is better than a decorative analytics page with fake metrics.

## Table And List Page Improvements

- Standardize list page toolbar layout:
  - Page title and short purpose.
  - Primary action.
  - Search.
  - Status/type filters where supported.
  - Result count and pagination summary.
- Add a common table shell with:
  - Consistent card header.
  - Optional toolbar slot.
  - Horizontal overflow behavior.
  - Hover state.
  - Empty state inside the table card.
  - Footer pagination.
- Normalize link styling for primary identifiers such as admission number, receipt number, voucher number, and journal number.
- Align money columns right.
- Keep status columns visually compact.
- Use sticky first column only if testing shows it helps financial tables without breaking mobile.

## Detail Page Improvements

- Create a common detail-card/description-list component instead of local repeated `DetailItem` functions.
- Put primary identifier, status, and high-risk action buttons in a consistent header area.
- Separate business facts from workflow controls:
  - Profile/details card.
  - Financial/accounting boundary card.
  - Notes/documents card.
  - Audit/workflow state card where relevant.
- Use callouts consistently for immutable/posted records.
- Use a stronger danger treatment for rollover execution, reversal, void, and refund-related actions.
- Show BS dates prominently where available, with AD dates as secondary context.

## Form Page Improvements

- Standardize form sections:
  - Context section: organization, branch, academic year, party.
  - Date/method section.
  - Allocation/lines section.
  - Notes/supporting metadata.
  - Review/submit section.
- Add a shared form section component with title, description, and optional warning.
- Improve financial forms:
  - Keep running totals visible near the allocation table.
  - Use clear debit/credit balance indicators.
  - Highlight out-of-balance and over-allocation states before submission.
  - Keep submit buttons disabled with visible reasons.
- Use consistent select styling through a reusable component or documented Tailwind class helper.
- Do not calculate final financial truth in the frontend; only show user-entered totals and backend-returned values.

## Status, Money, And Date Displays

- Expand `StatusBadge` into semantic variants:
  - Success: active, approved, paid, posted, completed.
  - Warning: pending, partial, on break, soft-closed.
  - Danger: rejected, voided, reversed, terminated.
  - Neutral: draft, inactive, cancelled, archived.
  - Info: submitted, open, inquiry.
- Add optional status dot or icon only if it remains accessible with text.
- Update `MoneyDisplay` to support:
  - Optional currency label.
  - Right-aligned table usage.
  - Negative amount styling for reports.
  - Consistent fallback for missing values.
- Add a small date display helper later:
  - Prefer BS date when present.
  - Show AD date as secondary text where useful.
  - Keep sortable AD values in table columns where required.

## Empty, Loading, Error, And Success States

- Loading states should use consistent skeleton-like blocks for tables and detail cards, not only text.
- Empty states should include one clear next action where the user has permission.
- Error states should distinguish:
  - Fetch/load failure.
  - Permission/role restriction.
  - Financial workflow validation failure.
  - Backend configuration error.
- Success states should use compact dismissible banners or inline confirmation panels.
- Avoid verbose development explanations in production UI.

## Responsive And Mobile Issues

Likely issues visible from code:

- Sidebar is hidden below `lg`, but no mobile navigation replacement exists.
- Table-heavy pages rely on horizontal scrolling but need verification for narrow screens.
- Page header actions may overflow on mobile when search and action buttons appear together.
- Large financial allocation forms need mobile stacking tests for select/input/button rows.
- Dashboard cards stack correctly, but content density and spacing need real mobile review.

Mobile targets:

- 375px width.
- 768px tablet.
- 1024px desktop.
- 1440px wide desktop.

## Accessibility Improvements

- Ensure all icon buttons have accessible labels once icons are added.
- Keep visible text labels for unfamiliar workflow actions.
- Verify focus rings on buttons, links, inputs, selects, and navigation items.
- Add `aria-current="page"` to active sidebar links.
- Improve loading state semantics and avoid layout shifts.
- Ensure error messages are associated with relevant fields where practical.
- Maintain color contrast for status badges, sidebar items, and disabled states.
- Ensure destructive/high-risk actions are not represented by color alone.

## Staged Implementation Plan

### Stage 1: Design Tokens And Primitives

Objective: Make visual consistency cheap before touching every page.

Tasks:

- Add CSS variables or Tailwind theme tokens for primary, background, border, text, muted text, success, warning, danger, info, card shadow, and radius.
- Refine `Button`, `TextInput`, `SearchInput`, `SimpleTable`, `PageHeader`, `StatusBadge`, `MoneyDisplay`, and state components.
- Add a shared card class/helper pattern.
- Add shared select and textarea styling helpers if a component is not created yet.

Expected output:

- Existing pages look cleaner without page-by-page rewrites.
- No workflow or API behavior changes.

### Stage 2: App Shell, Sidebar, And Topbar

Objective: Make the dashboard feel like a finished admin product.

Tasks:

- Add navigation grouping and active state improvements.
- Add mobile sidebar drawer.
- Add topbar breadcrumb support.
- Improve user/role/branch context display.
- Keep logout simple and accessible.

Expected output:

- Navigation is easier to scan.
- Mobile users can access the dashboard.
- Shell aligns more closely with the Volt-inspired direction without copying Volt.

### Stage 3: Dashboard Landing Page

Objective: Replace placeholder dashboard content with useful operational summaries.

Tasks:

- Add backend-backed summary cards where existing APIs support safe counts or totals.
- Add quick action/module shortcut cards.
- Add recent records sections using existing list APIs.
- Add high-risk workflow alerts only when backed by real data.

Expected output:

- `/dashboard` becomes a useful command center instead of a placeholder screen.

### Stage 4: List, Detail, And Form Consistency Pass

Objective: Normalize all existing workflow screens.

Tasks:

- Create shared list toolbar/table shell.
- Create shared detail card/description list.
- Create shared form section and financial totals panel.
- Apply to students, teachers, classes, billing, payroll, accounting, and academic rollover pages.
- Reduce repetitive development copy.

Expected output:

- Core pages feel cohesive and release-ready.
- Financial workflows remain visibly serious and backend-authoritative.

### Stage 5: Accessibility And Responsive Polish

Objective: Verify the UI under realistic screen sizes and assistive behavior.

Tasks:

- Run responsive checks at 375, 768, 1024, and 1440 widths.
- Verify keyboard navigation through shell, tables, forms, and high-risk actions.
- Add missing `aria-*` attributes and focus states.
- Capture Playwright screenshots if E2E tooling is available.
- Fix text overflow, cramped controls, and horizontal scroll problems.

Expected output:

- UI is usable on desktop and mobile.
- Accessibility issues are documented or fixed before release.

## Page Verification Checklist

Visually verify after each polish stage:

- `/login`
- `/forgot-password`
- `/reset-password`
- `/force-password-change`
- `/dashboard`
- `/dashboard/students`
- `/dashboard/students/[id]`
- `/dashboard/student-inquiries`
- `/dashboard/guardians`
- `/dashboard/families`
- `/dashboard/teachers`
- `/dashboard/teacher-contracts`
- `/dashboard/classes`
- `/dashboard/enrollments`
- `/dashboard/subjects`
- `/dashboard/billing/dues`
- `/dashboard/billing/invoices`
- `/dashboard/billing/payments`
- `/dashboard/billing/payments/[id]`
- `/dashboard/billing/payments/new`
- `/dashboard/billing/advance-balances`
- `/dashboard/billing/discounts`
- `/dashboard/billing/waivers`
- `/dashboard/billing/fines`
- `/dashboard/billing/refunds`
- `/dashboard/payroll/earnings`
- `/dashboard/payroll/earnings/[id]`
- `/dashboard/payroll/earnings/new`
- `/dashboard/payroll/payments`
- `/dashboard/payroll/payments/[id]`
- `/dashboard/payroll/payments/new`
- `/dashboard/payroll/payment-batches`
- `/dashboard/accounting/accounts`
- `/dashboard/accounting/journal-entries`
- `/dashboard/accounting/journal-entries/[id]`
- `/dashboard/accounting/journal-entries/new`
- `/dashboard/accounting/reports/trial-balance`
- `/dashboard/accounting/reports/general-ledger`
- `/dashboard/accounting/reports/profit-loss`
- `/dashboard/accounting/reports/balance-sheet`
- `/dashboard/academic-years`
- `/dashboard/academic-years/[id]`
- `/dashboard/academic-rollovers`
- `/dashboard/academic-rollovers/[id]`
- `/dashboard/academic-rollovers/new`

## Guardrails For The Polish Work

- Do not copy Volt code or import the Volt repository.
- Do not add Bootstrap or large UI dependencies.
- Do not change backend business logic, accounting logic, or API contracts.
- Do not move financial calculations into the frontend.
- Keep the UI quiet, dense, and work-focused.
- Make high-risk financial actions visually distinct and hard to trigger accidentally.
- Every UI change must pass lint, typecheck, tests, and build.
