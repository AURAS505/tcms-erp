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
    expect(screen.getByText("Admin User")).toBeInTheDocument();
  });

  it("does not render role navigation for a user without matching roles", () => {
    render(<Sidebar user={{ ...user, roles: [] }} />);

    expect(screen.queryByRole("link", { name: "Dashboard" })).not.toBeInTheDocument();
  });
});
