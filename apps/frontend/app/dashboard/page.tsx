"use client";

import Link from "next/link";
import { useAuth } from "@/hooks/useAuth";
import type { Role } from "@/types/auth";

interface DashboardCard {
  description: string;
  href: string;
  label: string;
  roles: Role[];
  tone: string;
}

const allStaffRoles: Role[] = [
  "super_admin",
  "institute_owner",
  "branch_admin",
  "accountant",
  "receptionist",
  "teacher",
  "auditor",
];

const financialRoles: Role[] = ["super_admin", "institute_owner", "branch_admin", "accountant", "auditor"];
const operationsRoles: Role[] = ["super_admin", "institute_owner", "branch_admin", "receptionist"];

const moduleShortcuts: DashboardCard[] = [
  {
    description: "Admissions, profiles, documents, and student status history.",
    href: "/dashboard/students",
    label: "Students",
    roles: ["super_admin", "institute_owner", "branch_admin", "receptionist", "auditor"],
    tone: "from-blue-50 to-white",
  },
  {
    description: "Class rooms, subjects, schedules, and enrollments.",
    href: "/dashboard/classes",
    label: "Classes",
    roles: ["super_admin", "institute_owner", "branch_admin", "receptionist", "teacher", "auditor"],
    tone: "from-cyan-50 to-white",
  },
  {
    description: "Fee plans, dues, invoices, payments, and adjustments.",
    href: "/dashboard/billing",
    label: "Billing",
    roles: ["super_admin", "institute_owner", "branch_admin", "accountant", "receptionist", "auditor"],
    tone: "from-emerald-50 to-white",
  },
  {
    description: "Teacher earnings, payment batches, and payment status.",
    href: "/dashboard/payroll",
    label: "Payroll",
    roles: financialRoles,
    tone: "from-amber-50 to-white",
  },
  {
    description: "Chart of accounts, journal entries, and financial reports.",
    href: "/dashboard/accounting",
    label: "Accounting",
    roles: financialRoles,
    tone: "from-violet-50 to-white",
  },
  {
    description: "Academic years, periods, BS date readiness, and rollover records.",
    href: "/dashboard/academic-years",
    label: "Academic Years",
    roles: allStaffRoles,
    tone: "from-slate-50 to-white",
  },
];

const summaryCards: DashboardCard[] = [
  {
    description: "Review student records, inquiries, guardian links, and documents.",
    href: "/dashboard/students",
    label: "Students",
    roles: operationsRoles,
    tone: "bg-blue-50 text-blue-700",
  },
  {
    description: "Open the billing workspace for dues, invoices, and payment status.",
    href: "/dashboard/billing/dues",
    label: "Open Dues",
    roles: ["super_admin", "institute_owner", "branch_admin", "accountant", "receptionist", "auditor"],
    tone: "bg-emerald-50 text-emerald-700",
  },
  {
    description: "Review teacher earning balances and payroll payment readiness.",
    href: "/dashboard/payroll/earnings",
    label: "Teacher Payables",
    roles: financialRoles,
    tone: "bg-amber-50 text-amber-700",
  },
  {
    description: "Open the ledger workspace for posted and draft journal activity.",
    href: "/dashboard/accounting/journal-entries",
    label: "Journal Entries",
    roles: financialRoles,
    tone: "bg-violet-50 text-violet-700",
  },
];

const quickActions: DashboardCard[] = [
  {
    description: "Capture a new payment draft for later approval and posting.",
    href: "/dashboard/billing/payments/new",
    label: "New Payment Draft",
    roles: ["super_admin", "institute_owner", "branch_admin", "accountant", "receptionist"],
    tone: "",
  },
  {
    description: "Prepare a manual journal entry for accounting review.",
    href: "/dashboard/accounting/journal-entries/new",
    label: "New Journal Entry",
    roles: ["super_admin", "institute_owner", "accountant"],
    tone: "",
  },
  {
    description: "Create a teacher earning draft for payroll processing.",
    href: "/dashboard/payroll/earnings/new",
    label: "New Teacher Earning",
    roles: ["super_admin", "institute_owner", "branch_admin", "accountant"],
    tone: "",
  },
  {
    description: "Prepare a new academic year rollover record.",
    href: "/dashboard/academic-rollovers/new",
    label: "Prepare Rollover",
    roles: ["super_admin", "institute_owner"],
    tone: "",
  },
];

const checklistItems = [
  "Review branch and academic year context before financial work.",
  "Use maker-checker approval for payments, journals, adjustments, and payroll.",
  "Keep BS dates visible for operations and AD dates available for reporting.",
  "Use ledger reports as the financial source of truth.",
];

function userHasAnyRole(userRoles: Role[], allowedRoles: Role[]) {
  return allowedRoles.some((role) => userRoles.includes(role));
}

function filterCards(cards: DashboardCard[], userRoles: Role[]) {
  return cards.filter((card) => userHasAnyRole(userRoles, card.roles));
}

export default function DashboardPage() {
  const { user } = useAuth();
  const userRoles = user?.roles.map((role) => role.code) ?? [];
  const visibleModules = filterCards(moduleShortcuts, userRoles);
  const visibleSummaries = filterCards(summaryCards, userRoles);
  const visibleActions = filterCards(quickActions, userRoles);
  const primaryRole = user?.roles[0]?.name ?? "Authenticated user";
  const branchCount = user?.branchAssignments.length ?? 0;

  return (
    <div className="space-y-6">
      <section className="overflow-hidden rounded-xl border border-[var(--tcms-color-border)] bg-white shadow-[var(--tcms-shadow-card)]">
        <div className="grid gap-6 p-6 lg:grid-cols-[1.6fr_1fr] lg:p-7">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.16em] text-[#0948B3]">TCMS ERP Control Center</p>
            <h1 className="mt-3 text-3xl font-bold tracking-normal text-[#262B40]">
              Welcome{user?.fullName ? `, ${user.fullName}` : ""}
            </h1>
            <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-600">
              Use this workspace to move between student operations, class management, billing, payroll, accounting, and
              academic year controls. Dashboard totals stay neutral until dedicated aggregate APIs are introduced.
            </p>
          </div>
          <div className="rounded-xl border border-slate-200 bg-[#F8FAFC] p-4">
            <p className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">Session context</p>
            <dl className="mt-4 space-y-3 text-sm">
              <div className="flex items-center justify-between gap-3">
                <dt className="text-slate-500">Role</dt>
                <dd className="text-right font-semibold text-[#262B40]">{primaryRole}</dd>
              </div>
              <div className="flex items-center justify-between gap-3">
                <dt className="text-slate-500">Branch access</dt>
                <dd className="text-right font-semibold text-[#262B40]">
                  {branchCount > 0 ? `${branchCount} assigned` : "Organization scope"}
                </dd>
              </div>
              <div className="flex items-center justify-between gap-3">
                <dt className="text-slate-500">Security</dt>
                <dd className="text-right font-semibold text-[#262B40]">Backend enforced</dd>
              </div>
            </dl>
          </div>
        </div>
      </section>

      <section aria-label="Dashboard summaries" className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {visibleSummaries.map((card) => (
          <Link
            className="group rounded-xl border border-[var(--tcms-color-border)] bg-white p-5 shadow-[var(--tcms-shadow-card)] transition hover:-translate-y-0.5 hover:shadow-[var(--tcms-shadow-elevated)]"
            href={card.href}
            key={card.label}
          >
            <div className={`inline-flex rounded-full px-3 py-1 text-xs font-bold ${card.tone}`}>View module</div>
            <h2 className="mt-4 text-base font-bold text-[#262B40]">{card.label}</h2>
            <p className="mt-2 text-sm leading-6 text-slate-600">{card.description}</p>
            <span className="mt-4 inline-flex text-sm font-semibold text-[#0948B3] group-hover:text-[#073a91]">
              Open workspace
            </span>
          </Link>
        ))}
      </section>

      <section>
        <div className="mb-3 flex items-end justify-between gap-4">
          <div>
            <h2 className="text-lg font-bold text-[#262B40]">Module Shortcuts</h2>
            <p className="mt-1 text-sm text-slate-600">Role-aware entry points for daily operations.</p>
          </div>
        </div>
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {visibleModules.map((card) => (
            <Link
              className={`group rounded-xl border border-[var(--tcms-color-border)] bg-gradient-to-br ${card.tone} p-5 shadow-[var(--tcms-shadow-card)] transition hover:-translate-y-0.5 hover:shadow-[var(--tcms-shadow-elevated)]`}
              href={card.href}
              key={card.label}
            >
              <div className="flex items-start justify-between gap-4">
                <div>
                  <h3 className="text-base font-bold text-[#262B40]">{card.label}</h3>
                  <p className="mt-2 text-sm leading-6 text-slate-600">{card.description}</p>
                </div>
                <span
                  aria-hidden="true"
                  className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-white text-sm font-bold text-[#0948B3] shadow-sm"
                >
                  {card.label.slice(0, 2).toUpperCase()}
                </span>
              </div>
              <span className="mt-4 inline-flex text-sm font-semibold text-[#0948B3] group-hover:text-[#073a91]">
                Open {card.label}
              </span>
            </Link>
          ))}
        </div>
      </section>

      <section className="grid gap-4 xl:grid-cols-[1.2fr_0.8fr]">
        <article className="rounded-xl border border-[var(--tcms-color-border)] bg-white p-5 shadow-[var(--tcms-shadow-card)]">
          <h2 className="text-lg font-bold text-[#262B40]">Operational Checklist</h2>
          <div className="mt-4 space-y-3">
            {checklistItems.map((item) => (
              <div className="flex gap-3 rounded-lg border border-slate-200 bg-[#F8FAFC] p-3" key={item}>
                <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-[#0948B3] text-xs font-bold text-white">
                  OK
                </span>
                <p className="text-sm leading-6 text-slate-600">{item}</p>
              </div>
            ))}
          </div>
        </article>

        <article className="rounded-xl border border-[var(--tcms-color-border)] bg-white p-5 shadow-[var(--tcms-shadow-card)]">
          <h2 className="text-lg font-bold text-[#262B40]">Quick Actions</h2>
          <p className="mt-1 text-sm leading-6 text-slate-600">Actions use existing routes and backend-guarded workflows.</p>
          <div className="mt-4 space-y-3">
            {visibleActions.length > 0 ? (
              visibleActions.map((action) => (
                <Link
                  className="block rounded-lg border border-slate-200 p-3 transition hover:border-[#0948B3] hover:bg-blue-50/50"
                  href={action.href}
                  key={action.label}
                >
                  <span className="text-sm font-bold text-[#262B40]">{action.label}</span>
                  <span className="mt-1 block text-sm leading-6 text-slate-600">{action.description}</span>
                </Link>
              ))
            ) : (
              <div className="rounded-lg border border-dashed border-slate-300 bg-slate-50 p-4 text-sm leading-6 text-slate-600">
                No quick actions are enabled for this role. Use the module shortcuts for read-only workspaces.
              </div>
            )}
          </div>
        </article>
      </section>
    </div>
  );
}
