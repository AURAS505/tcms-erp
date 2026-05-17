import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { Sidebar } from "@/components/layout/Sidebar";
import type { User } from "@/types/auth";

vi.mock("next/navigation", () => ({
  usePathname: () => "/dashboard",
}));

const user: User = {
  id: "user-1",
  email: "admin@tcms.test",
  username: "admin",
  fullName: "Admin User",
  forcePasswordChange: false,
  roles: [{ id: "role-1", code: "branch_admin", name: "Branch Admin", isReadOnly: false }],
  permissions: [],
  branchAssignments: [],
};

describe("Sidebar", () => {
  it("renders navigation items from shared role config", () => {
    render(<Sidebar user={user} />);

    const dashboardLink = screen.getByRole("link", { name: "Dashboard" });
    expect(dashboardLink).toHaveAttribute("href", "/dashboard");
    expect(screen.getByRole("link", { name: "Students" })).toHaveAttribute("href", "/dashboard/students");
    expect(screen.getByRole("link", { name: "Student Inquiries" })).toHaveAttribute(
      "href",
      "/dashboard/student-inquiries",
    );
    expect(screen.getByRole("link", { name: "Guardians" })).toHaveAttribute("href", "/dashboard/guardians");
    expect(screen.getByRole("link", { name: "Families" })).toHaveAttribute("href", "/dashboard/families");
    expect(screen.getByRole("link", { name: "Classes" })).toHaveAttribute("href", "/dashboard/classes");
    expect(screen.getByRole("link", { name: "Subjects" })).toHaveAttribute("href", "/dashboard/subjects");
    expect(screen.getByRole("link", { name: "Enrollments" })).toHaveAttribute("href", "/dashboard/enrollments");
    expect(screen.getByRole("link", { name: "Teachers" })).toHaveAttribute("href", "/dashboard/teachers");
    expect(screen.getByRole("link", { name: "Teacher Contracts" })).toHaveAttribute(
      "href",
      "/dashboard/teacher-contracts",
    );
    expect(screen.getByRole("link", { name: "Academic Years" })).toHaveAttribute("href", "/dashboard/academic-years");
    expect(screen.getByRole("link", { name: "Academic Rollovers" })).toHaveAttribute(
      "href",
      "/dashboard/academic-rollovers",
    );
    expect(screen.getByRole("link", { name: "Billing" })).toHaveAttribute("href", "/dashboard/billing");
    expect(screen.getByRole("link", { name: "Fee Plans" })).toHaveAttribute("href", "/dashboard/billing/fee-plans");
    expect(screen.getByRole("link", { name: "Dues" })).toHaveAttribute("href", "/dashboard/billing/dues");
    expect(screen.getByRole("link", { name: "Invoices" })).toHaveAttribute("href", "/dashboard/billing/invoices");
    expect(screen.getByRole("link", { name: "Payments" })).toHaveAttribute("href", "/dashboard/billing/payments");
    expect(screen.getByRole("link", { name: "Advance Balances" })).toHaveAttribute(
      "href",
      "/dashboard/billing/advance-balances",
    );
    expect(screen.getByRole("link", { name: "Discounts" })).toHaveAttribute("href", "/dashboard/billing/discounts");
    expect(screen.getByRole("link", { name: "Waivers" })).toHaveAttribute("href", "/dashboard/billing/waivers");
    expect(screen.getByRole("link", { name: "Fines" })).toHaveAttribute("href", "/dashboard/billing/fines");
    expect(screen.getByRole("link", { name: "Refunds" })).toHaveAttribute("href", "/dashboard/billing/refunds");
    expect(screen.getByRole("link", { name: "Payroll" })).toHaveAttribute("href", "/dashboard/payroll");
    expect(screen.getByRole("link", { name: "Teacher Earnings" })).toHaveAttribute("href", "/dashboard/payroll/earnings");
    expect(screen.getByRole("link", { name: "Teacher Payments" })).toHaveAttribute("href", "/dashboard/payroll/payments");
    expect(screen.getByRole("link", { name: "Payment Batches" })).toHaveAttribute(
      "href",
      "/dashboard/payroll/payment-batches",
    );
    expect(screen.getByRole("link", { name: "Accounting" })).toHaveAttribute("href", "/dashboard/accounting");
    expect(screen.getByRole("link", { name: "Chart of Accounts" })).toHaveAttribute(
      "href",
      "/dashboard/accounting/accounts",
    );
    expect(screen.getByRole("link", { name: "Journal Entries" })).toHaveAttribute(
      "href",
      "/dashboard/accounting/journal-entries",
    );
    expect(screen.getByRole("link", { name: "Accounting Documents" })).toHaveAttribute(
      "href",
      "/dashboard/accounting/documents",
    );
    expect(screen.getByRole("link", { name: "Trial Balance" })).toHaveAttribute(
      "href",
      "/dashboard/accounting/reports/trial-balance",
    );
    expect(screen.getByRole("link", { name: "General Ledger" })).toHaveAttribute(
      "href",
      "/dashboard/accounting/reports/general-ledger",
    );
    expect(screen.getByRole("link", { name: "Profit & Loss" })).toHaveAttribute(
      "href",
      "/dashboard/accounting/reports/profit-loss",
    );
    expect(screen.getByRole("link", { name: "Balance Sheet" })).toHaveAttribute(
      "href",
      "/dashboard/accounting/reports/balance-sheet",
    );
    expect(screen.getByText("Admin User")).toBeInTheDocument();
  });

  it("does not render role navigation for a user without matching roles", () => {
    render(<Sidebar user={{ ...user, roles: [] }} />);

    expect(screen.queryByRole("link", { name: "Dashboard" })).not.toBeInTheDocument();
  });
});
