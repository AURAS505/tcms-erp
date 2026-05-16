import type { Role } from "@/types/auth";

export interface NavItem {
  href: string;
  label: string;
  roles: Role[];
}

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
    href: "/dashboard",
    label: "Dashboard",
    roles: allRoles,
  },
  {
    href: "/dashboard/student-inquiries",
    label: "Student Inquiries",
    roles: allRoles,
  },
  {
    href: "/dashboard/students",
    label: "Students",
    roles: allRoles,
  },
  {
    href: "/dashboard/guardians",
    label: "Guardians",
    roles: allRoles,
  },
  {
    href: "/dashboard/families",
    label: "Families",
    roles: allRoles,
  },
  {
    href: "/dashboard/classes",
    label: "Classes",
    roles: allRoles,
  },
  {
    href: "/dashboard/subjects",
    label: "Subjects",
    roles: allRoles,
  },
  {
    href: "/dashboard/enrollments",
    label: "Enrollments",
    roles: allRoles,
  },
  {
    href: "/dashboard/teachers",
    label: "Teachers",
    roles: allRoles,
  },
  {
    href: "/dashboard/teacher-contracts",
    label: "Teacher Contracts",
    roles: allRoles,
  },
  {
    href: "/dashboard/billing",
    label: "Billing",
    roles: allRoles,
  },
  {
    href: "/dashboard/billing/fee-plans",
    label: "Fee Plans",
    roles: allRoles,
  },
  {
    href: "/dashboard/billing/dues",
    label: "Dues",
    roles: allRoles,
  },
  {
    href: "/dashboard/billing/invoices",
    label: "Invoices",
    roles: allRoles,
  },
  {
    href: "/dashboard/billing/payments",
    label: "Payments",
    roles: allRoles,
  },
  {
    href: "/dashboard/billing/advance-balances",
    label: "Advance Balances",
    roles: allRoles,
  },
  {
    href: "/dashboard/billing/discounts",
    label: "Discounts",
    roles: allRoles,
  },
  {
    href: "/dashboard/billing/waivers",
    label: "Waivers",
    roles: allRoles,
  },
  {
    href: "/dashboard/billing/fines",
    label: "Fines",
    roles: allRoles,
  },
  {
    href: "/dashboard/billing/refunds",
    label: "Refunds",
    roles: allRoles,
  },
  {
    href: "/dashboard/payroll",
    label: "Payroll",
    roles: allRoles,
  },
  {
    href: "/dashboard/payroll/earnings",
    label: "Teacher Earnings",
    roles: allRoles,
  },
  {
    href: "/dashboard/payroll/payments",
    label: "Teacher Payments",
    roles: allRoles,
  },
  {
    href: "/dashboard/payroll/payment-batches",
    label: "Payment Batches",
    roles: allRoles,
  },
  {
    href: "/dashboard/accounting",
    label: "Accounting",
    roles: allRoles,
  },
  {
    href: "/dashboard/accounting/accounts",
    label: "Chart of Accounts",
    roles: allRoles,
  },
  {
    href: "/dashboard/accounting/journal-entries",
    label: "Journal Entries",
    roles: allRoles,
  },
  {
    href: "/dashboard/accounting/documents",
    label: "Accounting Documents",
    roles: allRoles,
  },
  {
    href: "/dashboard/accounting/reports/trial-balance",
    label: "Trial Balance",
    roles: allRoles,
  },
  {
    href: "/dashboard/accounting/reports/general-ledger",
    label: "General Ledger",
    roles: allRoles,
  },
  {
    href: "/dashboard/accounting/reports/profit-loss",
    label: "Profit & Loss",
    roles: allRoles,
  },
  {
    href: "/dashboard/accounting/reports/balance-sheet",
    label: "Balance Sheet",
    roles: allRoles,
  },
];

export function getNavigationForRoles(roles: Role[]) {
  return navigationItems.filter((item) => item.roles.some((role) => roles.includes(role)));
}
