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
];

export function getNavigationForRoles(roles: Role[]) {
  return navigationItems.filter((item) => item.roles.some((role) => roles.includes(role)));
}
