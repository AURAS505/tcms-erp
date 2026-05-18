import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { Topbar } from "@/components/layout/Topbar";
import { useAuth } from "@/hooks/useAuth";
import type { User } from "@/types/auth";

const push = vi.fn();
const refresh = vi.fn();
const logout = vi.fn();

vi.mock("@/hooks/useAuth", () => ({
  useAuth: vi.fn(),
}));

vi.mock("next/navigation", () => ({
  usePathname: () => "/dashboard/billing/payments",
  useRouter: () => ({ push, refresh }),
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

describe("Topbar", () => {
  beforeEach(() => {
    push.mockReset();
    refresh.mockReset();
    logout.mockReset();
    vi.mocked(useAuth).mockReset();
  });

  it("renders route context and user role", () => {
    vi.mocked(useAuth).mockReturnValue({
      branchAssignments: [],
      error: null,
      hasPermission: vi.fn(),
      hasRole: vi.fn(),
      isAuthenticated: true,
      isLoading: false,
      login: vi.fn(),
      logout,
      permissions: [],
      refreshSession: vi.fn(),
      user,
    });

    render(<Topbar user={user} />);

    expect(screen.getByRole("heading", { name: "Payments" })).toBeInTheDocument();
    expect(screen.getByText("Branch Admin")).toBeInTheDocument();
  });

  it("calls the mobile menu handler", () => {
    const onMenuClick = vi.fn();
    vi.mocked(useAuth).mockReturnValue({
      branchAssignments: [],
      error: null,
      hasPermission: vi.fn(),
      hasRole: vi.fn(),
      isAuthenticated: true,
      isLoading: false,
      login: vi.fn(),
      logout,
      permissions: [],
      refreshSession: vi.fn(),
      user,
    });

    render(<Topbar onMenuClick={onMenuClick} user={user} />);
    fireEvent.click(screen.getByRole("button", { name: "Open navigation" }));

    expect(onMenuClick).toHaveBeenCalledTimes(1);
  });

  it("logs out through the auth hook", async () => {
    logout.mockResolvedValue(undefined);
    vi.mocked(useAuth).mockReturnValue({
      branchAssignments: [],
      error: null,
      hasPermission: vi.fn(),
      hasRole: vi.fn(),
      isAuthenticated: true,
      isLoading: false,
      login: vi.fn(),
      logout,
      permissions: [],
      refreshSession: vi.fn(),
      user,
    });

    render(<Topbar user={user} />);
    fireEvent.click(screen.getByRole("button", { name: "Logout" }));

    await waitFor(() => expect(logout).toHaveBeenCalledTimes(1));
    expect(push).toHaveBeenCalledWith("/login");
    expect(refresh).toHaveBeenCalledTimes(1);
  });
});
