import React from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { AuthProvider } from "@/components/providers/AuthProvider";
import { useAuth } from "@/hooks/useAuth";
import { authService } from "@/lib/auth";
import type { User } from "@/types/auth";

vi.mock("@/lib/auth", () => ({
  authService: {
    currentUser: vi.fn(),
    login: vi.fn(),
    logout: vi.fn(),
  },
}));

const user: User = {
  id: "user-1",
  email: "admin@tcms.test",
  username: "admin",
  fullName: "Admin User",
  forcePasswordChange: false,
  roles: [{ id: "role-1", code: "branch_admin", name: "Branch Admin", isReadOnly: false }],
  permissions: [{ id: "perm-1", code: "students.view", name: "View students", module: "students", isReadOnly: true }],
  branchAssignments: [{ id: "branch-assign-1", organizationId: "org-1", branchId: "branch-1", isPrimary: true }],
};

function renderWithAuthProvider(ui: React.ReactNode) {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });

  return render(
    <QueryClientProvider client={queryClient}>
      <AuthProvider>{ui}</AuthProvider>
    </QueryClientProvider>,
  );
}

function AuthProbe() {
  const {
    branchAssignments,
    error,
    hasPermission,
    hasRole,
    isAuthenticated,
    isLoading,
    logout,
    user: currentUser,
  } = useAuth();

  return (
    <div>
      <div>{isLoading ? "loading" : "settled"}</div>
      <div>{isAuthenticated ? "authenticated" : "guest"}</div>
      <div>{currentUser?.fullName ?? "No user"}</div>
      <div>{error?.message ?? "No error"}</div>
      <div>{hasRole("branch_admin") ? "has branch role" : "missing branch role"}</div>
      <div>{hasPermission("students.view") ? "can view students" : "cannot view students"}</div>
      <div>{branchAssignments[0]?.branchId ?? "no branch"}</div>
      <button onClick={() => void logout()} type="button">
        Logout
      </button>
    </div>
  );
}

describe("AuthProvider", () => {
  beforeEach(() => {
    vi.mocked(authService.currentUser).mockReset();
    vi.mocked(authService.login).mockReset();
    vi.mocked(authService.logout).mockReset();
  });

  it("loads current user successfully", async () => {
    vi.mocked(authService.currentUser).mockResolvedValue(user);

    renderWithAuthProvider(<AuthProbe />);

    expect(await screen.findByText("Admin User")).toBeInTheDocument();
    expect(screen.getByText("authenticated")).toBeInTheDocument();
    expect(screen.getByText("branch-1")).toBeInTheDocument();
  });

  it("handles unauthenticated state", async () => {
    vi.mocked(authService.currentUser).mockRejectedValue(new Error("Unauthorized"));

    renderWithAuthProvider(<AuthProbe />);

    await waitFor(() => expect(screen.getByText("Unauthorized")).toBeInTheDocument());
    expect(screen.getByText("guest")).toBeInTheDocument();
    expect(screen.getByText("No user")).toBeInTheDocument();
  });

  it("exposes role and permission helpers", async () => {
    vi.mocked(authService.currentUser).mockResolvedValue(user);

    renderWithAuthProvider(<AuthProbe />);

    expect(await screen.findByText("has branch role")).toBeInTheDocument();
    expect(screen.getByText("can view students")).toBeInTheDocument();
  });

  it("logout clears session state", async () => {
    vi.mocked(authService.currentUser).mockResolvedValue(user);
    vi.mocked(authService.logout).mockResolvedValue(null);

    renderWithAuthProvider(<AuthProbe />);

    expect(await screen.findByText("authenticated")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Logout" }));

    await waitFor(() => expect(screen.getByText("guest")).toBeInTheDocument());
    expect(screen.getByText("No user")).toBeInTheDocument();
  });
});
