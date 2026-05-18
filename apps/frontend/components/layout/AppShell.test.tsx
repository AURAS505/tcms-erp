import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { AppShell } from "@/components/layout/AppShell";
import { useAuth } from "@/hooks/useAuth";
import type { User } from "@/types/auth";

vi.mock("@/hooks/useAuth", () => ({
  useAuth: vi.fn(),
}));

vi.mock("next/navigation", () => ({
  usePathname: () => "/dashboard",
  useRouter: () => ({ push: vi.fn(), refresh: vi.fn() }),
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

describe("AppShell", () => {
  const baseAuth = {
    branchAssignments: [],
    error: null,
    hasPermission: vi.fn(),
    hasRole: vi.fn(),
    login: vi.fn(),
    logout: vi.fn(),
    permissions: [],
    refreshSession: vi.fn(),
  };

  beforeEach(() => {
    vi.mocked(useAuth).mockReset();
  });

  it("shows checking state before the auth request settles", () => {
    vi.mocked(useAuth).mockReturnValue({
      ...baseAuth,
      isAuthenticated: false,
      isLoading: true,
      user: null,
    });

    render(
      <AppShell>
        <div>Protected content</div>
      </AppShell>,
    );

    expect(screen.getByRole("status")).toHaveTextContent("Checking session...");
    expect(screen.queryByText("Protected content")).not.toBeInTheDocument();
  });

  it("shows auth-required state when unauthenticated", async () => {
    vi.mocked(useAuth).mockReturnValue({
      ...baseAuth,
      error: new Error("Unauthorized"),
      isAuthenticated: false,
      isLoading: false,
      user: null,
    });

    render(
      <AppShell>
        <div>Protected content</div>
      </AppShell>,
    );

    expect(await screen.findByText("Authentication required")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /go to login/i })).toHaveAttribute("href", "/login");
    expect(screen.queryByText("Protected content")).not.toBeInTheDocument();
  });

  it("renders children when authenticated", async () => {
    vi.mocked(useAuth).mockReturnValue({
      ...baseAuth,
      isAuthenticated: true,
      isLoading: false,
      user,
    });

    render(
      <AppShell>
        <div>Protected content</div>
      </AppShell>,
    );

    await waitFor(() => expect(screen.getByText("Protected content")).toBeInTheDocument());
    expect(screen.getAllByText("Admin User")).toHaveLength(2);
  });

  it("opens mobile navigation from the topbar button", async () => {
    vi.mocked(useAuth).mockReturnValue({
      ...baseAuth,
      isAuthenticated: true,
      isLoading: false,
      user,
    });

    render(
      <AppShell>
        <div>Protected content</div>
      </AppShell>,
    );

    fireEvent.click(screen.getByRole("button", { name: "Open navigation" }));

    expect(await screen.findByRole("dialog", { name: "Mobile navigation" })).toBeInTheDocument();
  });
});
