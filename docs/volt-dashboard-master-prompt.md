# Master Prompt: Volt React Dashboard — Full UI/UX Recreation

## Overview

Use this prompt (or any section of it) to recreate the Volt React Dashboard — a professional admin dashboard template. The design language is clean, minimal Bootstrap 5 with a white/light-gray background, indigo/blue primary accents, and a fixed left sidebar layout.

---

## Global Design System

**Color Palette:**
- Primary: `#262B40` (dark navy sidebar bg)
- Accent / CTA: `#0948B3` (indigo blue — buttons, links, highlights)
- Secondary Accent: `#F0F3FF` (light lavender — active sidebar item bg)
- Success: `#05A677`
- Warning: `#F5A623`
- Danger: `#FA5252`
- Info: `#1E90FF`
- Body Background: `#F5F8FB` (very light blue-gray)
- Card Background: `#FFFFFF`
- Sidebar Text: `#C5CDE4` (muted light)
- Sidebar Active Text: `#FFFFFF`
- Border Color: `#E5E7EB`
- Text Primary: `#262B40`
- Text Muted: `#93A5BE`

**Typography:**
- Font Family: `Nunito Sans, system-ui, sans-serif`
- Base Size: 14px
- Headings: 500–700 weight
- Sidebar Nav Items: 14px, weight 500
- Card Titles: 16px, weight 600
- Metric Numbers: 24–32px, weight 700

**Layout:**
- Fixed left sidebar: 260px wide
- Top navbar: 60px tall
- Main content area: fills remaining width, `padding: 24px 28px`
- Card grid: Bootstrap-style 12-column grid
- Card border-radius: 8px
- Card box-shadow: `0 2px 18px rgba(38, 43, 64, 0.08)`

---

## Component 1 — Sidebar Navigation

Build a fixed left sidebar (260px wide, full viewport height) with:

**Header:**
- Logo area at top: flame/bolt icon + "Volt" wordmark in white, bold
- Below logo: user avatar (40px circle), username "Neil Sims", email "neil.sims@flowbite.com" in small muted text

**Navigation sections (with Lucide/Feather icons):**
- **Dashboard** section:
  - Overview (chart-bar icon) — active state with indigo bg pill
  - Traffic & Engagement (chart-line icon)
- **Components** section header (uppercase, muted, 11px):
  - Accordion, Alerts, Badges, Breadcrumbs, Buttons, Cards, Forms, Modals, Navs, Pagination, Popovers, Progress, Tables, Tabs, Tooltips, Widgets — all collapsible under a "Bootstrap UI" group with chevron toggle
- **Plugins** section header:
  - Calendar, Datatables, Sweetalert, Notyf
- **Documentation** section header:
  - Getting Started, Changelog

**Footer area:**
- "Upgrade to Pro" card inside sidebar (indigo bg, white text, "Upgrade" button)

**Active state:** rounded pill/badge on left side, white text, indigo `#0948B3` background
**Hover state:** slightly lighter indigo bg, text becomes white

---

## Component 2 — Top Navbar

Fixed top bar (60px, white bg, subtle bottom border) containing:

**Left:** Hamburger/toggle icon to collapse sidebar + breadcrumb ("Dashboard / Overview")

**Right side (flex row, gap 16px):**
1. Search bar (input with magnifier icon, rounded, light gray bg, placeholder "Search")
2. Notification bell icon with badge count (red dot, number "4")
3. Messages icon with badge
4. Settings gear icon
5. User avatar dropdown (40px circle, name "Neil Sims" + chevron down)

---

## Component 3 — Dashboard Overview Page

### Section A — Stat Counter Cards (top row, 4 columns)

Each card: white bg, 8px radius, subtle shadow, padding 20px, flex row.

Build 4 counter cards:

| Card | Icon (circle bg) | Metric | Value | Change |
|------|-----------------|--------|-------|--------|
| Customers | purple circle, users icon | Total Customers | 5,355 | +2.5% ↑ green |
| Revenue | blue circle, dollar icon | Revenue | $4,550 | +1.8% ↑ green |
| Total Orders | green circle, shopping-cart | Total Orders | 238 | -0.3% ↓ red |
| Growth | orange circle, trending-up | Growth | 18.2% | +3.4% ↑ green |

Card structure:
- Left: colored circle (40px) with white icon inside
- Right: metric label (14px muted), big bold number (28px), change badge (green/red pill, arrow + %)

---

### Section B — Sales Value Chart (large, 8-col)

Large card titled **"Sales Value"** with:
- Header row: title left, time period tabs right ("Day" | "Week" | "Month") as button group
- Subtext: "Total orders 238" with green +18.2% badge
- **Area chart** (Chart.js or Recharts):
  - X-axis: months Jan–Dec
  - Y-axis: $0–$10,000
  - Two lines: "Sales" (indigo `#0948B3`, filled area below) and "Referral" (orange `#F5A623`, dashed)
  - Smooth curved lines (tension: 0.4)
  - Tooltip on hover showing exact values
  - Chart height: 250px

---

### Section C — Ranking Card (4-col, right of chart)

Card titled **"Ranking"** with:
- Big centered percentage: **"25.3%"** in 40px bold
- Subtitle: "Worldwide share"
- Circular progress ring: SVG circle, 120px, indigo stroke, showing ~25% filled
- Below ring: two stat rows:
  - "Change" — +12.5% (green)
  - "Monthly Goal" — 67% progress bar (indigo fill)
- Bottom: "View full report →" link in indigo

---

### Section D — Transactions Table (8-col)

Card titled **"Latest Transactions"** with "See all" link in header.

Table with columns: **#** | **Bill For** | **Issue Date** | **Due Date** | **Total** | **Status**

Sample rows:
```
#321 | Platinum Subscription | 1 May 2020 | 1 Jun 2020 | $2,500 | Paid (green badge)
#322 | Platinum Subscription | 2 May 2020 | 2 Jun 2020 | $2,500 | Due (orange badge)
#323 | Platinum Subscription | 3 May 2020 | 3 Jun 2020 | $2,500 | Cancelled (red badge)
#324 | Platinum Subscription | 4 May 2020 | 4 Jun 2020 | $2,500 | Paid (green badge)
#325 | Platinum Subscription | 5 May 2020 | 5 Jun 2020 | $2,500 | Due (orange badge)
```

Badge styles: `Paid` = green pill, `Due` = orange pill, `Cancelled` = red pill

---

### Section E — Team Members Card (4-col)

Card titled **"Team Members"** with "See all" link.

List of 5 team members, each row:
- Avatar (36px circle with initials or image)
- Name (14px bold) + role (12px muted text)
- Online indicator dot (green = online, gray = offline)

Members:
1. Neil Sims — Product Manager (green dot)
2. Bonnie Green — Web Designer (green dot)
3. Jese Leos — React Developer (gray dot)
4. Joseph Mcfall — Vue.js Developer (gray dot)
5. Helene Engels — Angular Developer (green dot)

---

### Section F — Progress Track (full width row, below)

Card titled **"Traffic & Conversions"**. Two stat blocks side by side:

Left block — Traffic Sources (horizontal bar chart):
- Social: 70% — indigo bar
- Organic: 50% — green bar
- Direct: 35% — orange bar
- Referral: 20% — red bar

Right block — Top Pages table:
| Page | Views | Bounce |
|------|-------|--------|
| /index.html | 3,201 | 40.2% |
| /about.html | 1,456 | 24.1% |
| /contact.html | 987 | 35.5% |
| /blog.html | 756 | 18.2% |

---

## Component 4 — Transactions Page

Full-width card with:
- **Page header:** "Transactions" title + date range picker button ("1 Apr 2020 – 30 Apr 2020") + "Export CSV" button
- **Filter bar:** Search input + Status dropdown (All / Paid / Due / Cancelled) + Type dropdown
- **Full table** with sortable columns: Invoice # | Customer | Country | Date | Amount | Status | Actions
- Pagination at bottom: "Showing 1–10 of 238" + prev/next buttons + page number pills

---

## Component 5 — Settings Page

Two-column layout (8-col form + 4-col sidebar info card):

**General Info form** (left card, titled "General Info"):
- First Name, Last Name (inline row)
- Date of Birth (date picker)
- Email, Phone, Location fields
- Biography textarea
- "Save All" primary button (indigo)

**Profile card** (right, 4-col):
- Large avatar (80px)
- "Upload Photo" button (secondary outlined)
- Username, join date, verified badge
- Stats: Posts, Followers, Following

---

## Component 6 — Authentication Pages

### Sign In Page
Full-viewport centered card (400px wide):
- Logo at top
- Title "Sign in to our platform"
- Email input (with envelope icon left)
- Password input (with lock icon + show/hide toggle)
- "Remember me" checkbox + "Lost password?" link (right-aligned)
- Large indigo "Sign In" button (full width)
- "Not registered?" + "Create account" link

### Sign Up Page
Similar card:
- First + Last name (2-col)
- Email, Password, Confirm Password
- Terms & Conditions checkbox
- "Create Account" primary button
- "Already have account? Sign in" link

### Forgot Password Page
Simple card:
- "Forgot your password?" title
- Subtitle: "We'll send a password reset link to your email"
- Email input
- "Recover Password" button

---

## Component 7 — Bootstrap Tables Page

Card with:
- Header: "Bootstrap Table" + small description
- Striped table with:
  - Checkbox column (first)
  - Columns: Name, Age, Email, Status, Actions
  - Hover highlight
  - Striped rows (alternating light gray)
  - Action buttons: Edit (blue), Delete (red) — small icon buttons

---

## Component 8 — 404 / 500 Error Pages

Centered layout (no sidebar for these):
- Large illustrated SVG number ("404" or "500")
- Headline: "Page Not Found" / "Server Error"
- Description paragraph
- "Go Back Home" primary button

---

## Component 9 — Lock Screen Page

Centered card:
- User avatar (80px)
- "Hi, Neil Sims"
- "Enter your password to unlock the screen"
- Password input
- "Unlock Screen" button

---

## Implementation Notes

**Tech Stack (to match original):**
- React.js + react-bootstrap
- Bootstrap 5 CSS (or Tailwind equivalent)
- Recharts or Chart.js for charts
- react-router-dom for navigation
- Feather Icons or Heroicons

**File Structure to Create:**
```
src/
├── components/
│   ├── Sidebar.jsx
│   ├── Navbar.jsx
│   ├── Footer.jsx
│   ├── Widgets.jsx      (CounterCard, RankingCard, TeamMember, etc.)
│   ├── Charts.jsx       (SalesAreaChart, TrafficChart)
│   └── Tables.jsx       (TransactionsTable, BootstrapTable)
├── pages/
│   ├── dashboard/
│   │   └── DashboardOverview.jsx
│   ├── Transactions.jsx
│   ├── Settings.jsx
│   └── examples/
│       ├── SignIn.jsx
│       ├── SignUp.jsx
│       ├── ForgotPassword.jsx
│       ├── ResetPassword.jsx
│       ├── LockScreen.jsx
│       ├── NotFound.jsx
│       └── ServerError.jsx
├── data/
│   ├── transactions.js
│   ├── teamMembers.js
│   └── charts.js
└── routes.js
```

**Key UX Patterns:**
- Sidebar collapses to icons-only on mobile (hamburger toggle)
- All cards have consistent `border-radius: 8px` and `box-shadow: 0 2px 18px rgba(38,43,64,0.08)`
- Tables have hover highlight (`background: #F0F3FF`) and no outer border (borderless style)
- Status badges always use pill shape (`border-radius: 20px`, padding `4px 12px`)
- All buttons use indigo primary `#0948B3` with white text and hover darkens to `#0938A0`
- Form inputs: light gray bg `#F3F4F6`, no border until focus, then indigo `1px solid #0948B3` focus ring
- Charts always include a legend and export button in the card header
- All pages are responsive: sidebar hides on mobile, grid stacks to 1-col

---

## Quick Single-Page Prompt (for fast generation)

> "Create a React admin dashboard page that exactly matches the Volt React Dashboard design. Use a dark navy sidebar (#262B40) with white text and an indigo active state (#0948B3), a white top navbar with search + notification icons, and a main content area on a light blue-gray background (#F5F8FB). The dashboard overview page should include: (1) four stat counter cards in a row showing Customers 5355, Revenue $4550, Orders 238, Growth 18.2% with colored icon circles and green/red percentage change badges; (2) a large Sales Value area chart card showing Jan–Dec data with two datasets and a Day/Week/Month tab switcher; (3) a Ranking card with a circular SVG progress ring showing 25.3%; (4) a Latest Transactions table with Paid/Due/Cancelled status badges; (5) a Team Members list with avatar initials, names, roles, and online status dots. Use Nunito Sans font, Bootstrap-style card shadows, 8px border radius on all cards, and clean minimal styling throughout."
