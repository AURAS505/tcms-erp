# 0059 - Frontend Design Tokens And UI Primitives

Date: 2026-05-18

## Status

Accepted

## Context

Step 24A identified that the TCMS ERP frontend already had a functional Volt-inspired dashboard foundation, but shared UI primitives still relied on repeated inline Tailwind values and a narrow set of visual states.

The next polish stage needed to improve visual consistency without changing backend workflows, financial calculations, accounting behavior, API contracts, or adding large UI dependencies.

## Decision

Add global design tokens in `apps/frontend/app/globals.css` and polish existing reusable UI primitives:

- Background, card, text, muted text, border, primary, success, warning, danger, info, shadow, radius, and focus-ring tokens.
- Shared helper classes:
  - `tcms-card`
  - `tcms-focus`
  - `tcms-control`
- Button variants:
  - `primary`
  - `secondary`
  - `danger`
  - `ghost`
- Improved text input accessibility with optional help text, error text, `aria-describedby`, and invalid state.
- More consistent page header spacing and responsive action wrapping.
- More polished table shell, header, row hover, and optional empty table state.
- More complete status badge color mapping with bordered pill styling.
- Money display styling with tabular numbers and negative-value color treatment.
- More polished empty, loading, and error states.

## Volt Reference Use

`docs/volt-dashboard-master-prompt.md` was used only as a visual reference for:

- Navy/indigo/light-gray palette.
- Card radius and shadow rhythm.
- Compact admin table styling.
- Pill-style statuses.
- Clear focus and control hierarchy.

No Volt source code was copied, no Volt repository was imported, Bootstrap was not added, and no large UI dependency was introduced.

## Consequences

- Existing pages inherit a cleaner visual baseline through shared primitives.
- Future UI work can use shared tokens instead of repeating raw hex colors and shadows.
- The new `danger` button variant is available for later high-risk financial actions.
- Existing component APIs remain backward compatible.
- No backend, business, workflow, accounting, or API behavior changed.

## Follow-Up

- Stage 2 should polish `AppShell`, `Sidebar`, and `Topbar`.
- Stage 4 should replace repeated local detail item markup with shared detail/description components.
- A later accessibility pass should verify keyboard flow and focus visibility across all high-risk financial workflows.
