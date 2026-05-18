import React from "react";
import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import DashboardPage from "@/app/dashboard/page";
import { useAuth } from "@/hooks/useAuth";
import type { Role, User } from "@/types/auth";

vi.mock("@/hooks/useAuth", () => ({
  useAuth: vi.fn(),
}));

function makeUser(role: Role, name = "Branch User"): User {
  return {
    id: "user-1",
    email: "user@tcms.test",
    username: "user",
    fullName: name,
    forcePasswordChange: false,
    roles: [{ id: "role-1", code: role, name: role.replaceAll("_", " "), isReadOnly: role === "auditor" }],
    permissions: [],
    branchAssignments: [{ id: "branch-1", branchId: "branch-1", organizationId: "org-1", isPrimary: true }],
  };
}

describe("DashboardPage", () => {
  beforeEach(() => {
    vi.mocked(useAuth).mockReset();
  });

  it("renders the polished dashboard landing page", () => {
    vi.mocked(useAuth).mockReturnValue({
      branchAssignments: [],
      error: null,
      hasPermission: vi.fn(),
      hasRole: vi.fn(),
      isAuthenticated: true,
      isLoading: false,
      login: vi.fn(),
      logout: vi.fn(),
      permissions: [],
      refreshSession: vi.fn(),
      user: makeUser("branch_admin", "Admin User"),
    });

    render(<DashboardPage />);

    expect(screen.getByRole("heading", { name: "Welcome, Admin User" })).toBeInTheDocument();
    expect(screen.getByText("TCMS ERP Control Center")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /Open Students/i })).toHaveAttribute("href", "/dashboard/students");
    expect(screen.getByRole("link", { name: /Open Classes/i })).toHaveAttribute("href", "/dashboard/classes");
    expect(screen.getByRole("link", { name: /Open Billing/i })).toHaveAttribute("href", "/dashboard/billing");
    expect(screen.getByText("Operational Checklist")).toBeInTheDocument();
  });

  it("shows accountant financial shortcuts and hides student operations summary", () => {
    vi.mocked(useAuth).mockReturnValue({
      branchAssignments: [],
      error: null,
      hasPermission: vi.fn(),
      hasRole: vi.fn(),
      isAuthenticated: true,
      isLoading: false,
      login: vi.fn(),
      logout: vi.fn(),
      permissions: [],
      refreshSession: vi.fn(),
      user: makeUser("accountant", "Accountant User"),
    });

    render(<DashboardPage />);

    expect(screen.getByRole("link", { name: /Open Accounting/i })).toHaveAttribute("href", "/dashboard/accounting");
    expect(screen.getByRole("link", { name: /New Journal Entry/i })).toHaveAttribute(
      "href",
      "/dashboard/accounting/journal-entries/new",
    );
    expect(screen.queryByRole("link", { name: /Open Students/i })).not.toBeInTheDocument();
  });

  it("limits teacher shortcuts to class and academic workspaces", () => {
    vi.mocked(useAuth).mockReturnValue({
      branchAssignments: [],
      error: null,
      hasPermission: vi.fn(),
      hasRole: vi.fn(),
      isAuthenticated: true,
      isLoading: false,
      login: vi.fn(),
      logout: vi.fn(),
      permissions: [],
      refreshSession: vi.fn(),
      user: makeUser("teacher", "Teacher User"),
    });

    render(<DashboardPage />);

    expect(screen.getByRole("link", { name: /Open Classes/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /Open Academic Years/i })).toBeInTheDocument();
    expect(screen.queryByRole("link", { name: /Open Billing/i })).not.toBeInTheDocument();
    expect(screen.getByText(/No quick actions are enabled for this role/i)).toBeInTheDocument();
  });

  it("keeps auditor access read-oriented", () => {
    vi.mocked(useAuth).mockReturnValue({
      branchAssignments: [],
      error: null,
      hasPermission: vi.fn(),
      hasRole: vi.fn(),
      isAuthenticated: true,
      isLoading: false,
      login: vi.fn(),
      logout: vi.fn(),
      permissions: [],
      refreshSession: vi.fn(),
      user: makeUser("auditor", "Auditor User"),
    });

    render(<DashboardPage />);

    expect(screen.getByRole("link", { name: /Open Accounting/i })).toBeInTheDocument();
    expect(screen.queryByRole("link", { name: /New Payment Draft/i })).not.toBeInTheDocument();
    expect(screen.queryByRole("link", { name: /New Journal Entry/i })).not.toBeInTheDocument();
  });
});
