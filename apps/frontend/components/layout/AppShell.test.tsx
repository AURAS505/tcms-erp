import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { AppShell } from "@/components/layout/AppShell";
import { authService } from "@/lib/auth";
import type { User } from "@/types/auth";

vi.mock("@/lib/auth", () => ({
  authService: {
    currentUser: vi.fn(),
    logout: vi.fn(),
  },
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
  beforeEach(() => {
    vi.mocked(authService.currentUser).mockReset();
  });

  it("shows checking state before the auth request settles", () => {
    vi.mocked(authService.currentUser).mockReturnValue(new Promise(() => undefined));

    render(
      <AppShell>
        <div>Protected content</div>
      </AppShell>,
    );

    expect(screen.getByRole("status")).toHaveTextContent("Checking session...");
    expect(screen.queryByText("Protected content")).not.toBeInTheDocument();
  });

  it("shows auth-required state when unauthenticated", async () => {
    vi.mocked(authService.currentUser).mockRejectedValue(new Error("Unauthorized"));

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
    vi.mocked(authService.currentUser).mockResolvedValue(user);

    render(
      <AppShell>
        <div>Protected content</div>
      </AppShell>,
    );

    await waitFor(() => expect(screen.getByText("Protected content")).toBeInTheDocument());
    expect(screen.getAllByText("Admin User")).toHaveLength(2);
  });
});
