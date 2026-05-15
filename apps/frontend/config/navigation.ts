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
];

export function getNavigationForRoles(roles: Role[]) {
  return navigationItems.filter((item) => item.roles.some((role) => roles.includes(role)));
}
