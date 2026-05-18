import type { Role } from "@/types/auth";

export interface NavItem {
  href: string;
  label: string;
  group: NavGroup;
  roles: Role[];
}

export interface NavGroupConfig {
  label: NavGroup;
  description: string;
}

export type NavGroup = "Overview" | "People" | "Academic" | "Classes" | "Billing" | "Payroll" | "Accounting";

const allRoles: Role[] = [
  "super_admin",
  "institute_owner",
  "branch_admin",
  "accountant",
  "receptionist",
  "teacher",
  "auditor",
];

export const navigationItems: NavItem[] = [
  {
    group: "Overview",
    href: "/dashboard",
    label: "Dashboard",
    roles: allRoles,
  },
  {
    group: "People",
    href: "/dashboard/student-inquiries",
    label: "Student Inquiries",
    roles: allRoles,
  },
  {
    group: "People",
    href: "/dashboard/students",
    label: "Students",
    roles: allRoles,
  },
  {
    group: "People",
    href: "/dashboard/guardians",
    label: "Guardians",
    roles: allRoles,
  },
  {
    group: "People",
    href: "/dashboard/families",
    label: "Families",
    roles: allRoles,
  },
  {
    group: "Classes",
    href: "/dashboard/classes",
    label: "Classes",
    roles: allRoles,
  },
  {
    group: "Classes",
    href: "/dashboard/subjects",
    label: "Subjects",
    roles: allRoles,
  },
  {
    group: "Classes",
    href: "/dashboard/enrollments",
    label: "Enrollments",
    roles: allRoles,
  },
  {
    group: "People",
    href: "/dashboard/teachers",
    label: "Teachers",
    roles: allRoles,
  },
  {
    group: "People",
    href: "/dashboard/teacher-contracts",
    label: "Teacher Contracts",
    roles: allRoles,
  },
  {
    group: "Academic",
    href: "/dashboard/academic-years",
    label: "Academic Years",
    roles: allRoles,
  },
  {
    group: "Academic",
    href: "/dashboard/academic-rollovers",
    label: "Academic Rollovers",
    roles: allRoles,
  },
  {
    group: "Billing",
    href: "/dashboard/billing",
    label: "Billing",
    roles: allRoles,
  },
  {
    group: "Billing",
    href: "/dashboard/billing/fee-plans",
    label: "Fee Plans",
    roles: allRoles,
  },
  {
    group: "Billing",
    href: "/dashboard/billing/dues",
    label: "Dues",
    roles: allRoles,
  },
  {
    group: "Billing",
    href: "/dashboard/billing/invoices",
    label: "Invoices",
    roles: allRoles,
  },
  {
    group: "Billing",
    href: "/dashboard/billing/payments",
    label: "Payments",
    roles: allRoles,
  },
  {
    group: "Billing",
    href: "/dashboard/billing/advance-balances",
    label: "Advance Balances",
    roles: allRoles,
  },
  {
    group: "Billing",
    href: "/dashboard/billing/discounts",
    label: "Discounts",
    roles: allRoles,
  },
  {
    group: "Billing",
    href: "/dashboard/billing/waivers",
    label: "Waivers",
    roles: allRoles,
  },
  {
    group: "Billing",
    href: "/dashboard/billing/fines",
    label: "Fines",
    roles: allRoles,
  },
  {
    group: "Billing",
    href: "/dashboard/billing/refunds",
    label: "Refunds",
    roles: allRoles,
  },
  {
    group: "Payroll",
    href: "/dashboard/payroll",
    label: "Payroll",
    roles: allRoles,
  },
  {
    group: "Payroll",
    href: "/dashboard/payroll/earnings",
    label: "Teacher Earnings",
    roles: allRoles,
  },
  {
    group: "Payroll",
    href: "/dashboard/payroll/payments",
    label: "Teacher Payments",
    roles: allRoles,
  },
  {
    group: "Payroll",
    href: "/dashboard/payroll/payment-batches",
    label: "Payment Batches",
    roles: allRoles,
  },
  {
    group: "Accounting",
    href: "/dashboard/accounting",
    label: "Accounting",
    roles: allRoles,
  },
  {
    group: "Accounting",
    href: "/dashboard/accounting/accounts",
    label: "Chart of Accounts",
    roles: allRoles,
  },
  {
    group: "Accounting",
    href: "/dashboard/accounting/journal-entries",
    label: "Journal Entries",
    roles: allRoles,
  },
  {
    group: "Accounting",
    href: "/dashboard/accounting/documents",
    label: "Accounting Documents",
    roles: allRoles,
  },
  {
    group: "Accounting",
    href: "/dashboard/accounting/reports/trial-balance",
    label: "Trial Balance",
    roles: allRoles,
  },
  {
    group: "Accounting",
    href: "/dashboard/accounting/reports/general-ledger",
    label: "General Ledger",
    roles: allRoles,
  },
  {
    group: "Accounting",
    href: "/dashboard/accounting/reports/profit-loss",
    label: "Profit & Loss",
    roles: allRoles,
  },
  {
    group: "Accounting",
    href: "/dashboard/accounting/reports/balance-sheet",
    label: "Balance Sheet",
    roles: allRoles,
  },
];

export const navigationGroups: NavGroupConfig[] = [
  { label: "Overview", description: "Workspace" },
  { label: "People", description: "Students, guardians, teachers" },
  { label: "Academic", description: "Years and periods" },
  { label: "Classes", description: "Subjects and enrollments" },
  { label: "Billing", description: "Dues, invoices, payments" },
  { label: "Payroll", description: "Teacher earnings and payments" },
  { label: "Accounting", description: "Ledger and reports" },
];

export function getNavigationForRoles(roles: Role[]) {
  return navigationItems.filter((item) => item.roles.some((role) => roles.includes(role)));
}

export function getNavigationGroupsForRoles(roles: Role[]) {
  const items = getNavigationForRoles(roles);

  return navigationGroups
    .map((group) => ({
      ...group,
      items: items.filter((item) => item.group === group.label),
    }))
    .filter((group) => group.items.length > 0);
}
