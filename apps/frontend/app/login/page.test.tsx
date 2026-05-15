import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import LoginPage from "@/app/login/page";
import { authService } from "@/lib/auth";
import type { User } from "@/types/auth";

vi.mock("@/lib/auth", () => ({
  authService: {
    login: vi.fn(),
  },
}));

const push = vi.fn();
const refresh = vi.fn();

vi.mock("next/navigation", () => ({
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

describe("LoginPage", () => {
  beforeEach(() => {
    vi.mocked(authService.login).mockReset();
    push.mockReset();
    refresh.mockReset();
  });

  it("validates required fields", async () => {
    render(<LoginPage />);

    fireEvent.click(screen.getByRole("button", { name: /sign in/i }));

    expect(await screen.findByText("Email or username is required")).toBeInTheDocument();
    expect(screen.getByText("Password is required")).toBeInTheDocument();
    expect(authService.login).not.toHaveBeenCalled();
  });

  it("redirects to dashboard after successful login", async () => {
    vi.mocked(authService.login).mockResolvedValue(user);
    render(<LoginPage />);

    fireEvent.change(screen.getByLabelText(/email or username/i), { target: { value: "admin@tcms.test" } });
    fireEvent.change(screen.getByLabelText(/^password$/i), { target: { value: "StrongPass123!" } });
    fireEvent.click(screen.getByRole("button", { name: /sign in/i }));

    await waitFor(() => expect(push).toHaveBeenCalledWith("/dashboard"));
    expect(refresh).toHaveBeenCalled();
  });

  it("redirects to force password change when required", async () => {
    vi.mocked(authService.login).mockResolvedValue({ ...user, forcePasswordChange: true });
    render(<LoginPage />);

    fireEvent.change(screen.getByLabelText(/email or username/i), { target: { value: "admin@tcms.test" } });
    fireEvent.change(screen.getByLabelText(/^password$/i), { target: { value: "TempPass123!" } });
    fireEvent.click(screen.getByRole("button", { name: /sign in/i }));

    await waitFor(() => expect(push).toHaveBeenCalledWith("/force-password-change"));
    expect(refresh).toHaveBeenCalled();
  });
});
