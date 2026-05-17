import { afterEach, describe, expect, it, vi } from "vitest";
import { clearCsrfTokenCache } from "@/lib/api-client";
import { authService } from "@/lib/auth";

const backendUser = {
  id: "user-1",
  username: "admin",
  email: "admin@tcms.test",
  full_name: "Admin User",
  force_password_change: false,
  roles: [{ id: "role-1", code: "branch_admin", name: "Branch Admin", is_read_only: false }],
  permissions: [{ id: "perm-1", code: "students.view", name: "View students", module: "students", is_read_only: true }],
  branch_assignments: [{ id: "branch-assignment-1", organization_id: "org-1", branch_id: "branch-1", is_primary: true }],
};

const mockFetch = (data: unknown) => {
  const fetchMock = vi.fn((url: string, _init?: RequestInit) => Promise.resolve({
    ok: true,
    status: 200,
    json: vi.fn().mockResolvedValue({
      success: true,
      data: url.endsWith("/api/v1/auth/csrf/") ? { csrf_token: "csrf-token-1" } : data,
      errors: null,
      meta: {},
    }),
  }));
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
};

describe("authService", () => {
  afterEach(() => {
    clearCsrfTokenCache();
    vi.unstubAllGlobals();
  });

  it("maps login identifier to username_or_email", async () => {
    const fetchMock = mockFetch(backendUser);

    await authService.login({ identifier: "admin@tcms.test", password: "secret" });

    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/api/v1/auth/login/",
      expect.objectContaining({
        method: "POST",
        credentials: "include",
        headers: expect.any(Headers),
        body: JSON.stringify({ username_or_email: "admin@tcms.test", password: "secret" }),
      }),
    );
    const loginCall = fetchMock.mock.calls.find(([url]) => url === "http://localhost:8000/api/v1/auth/login/");
    expect(loginCall).toBeDefined();
    const loginHeaders = loginCall?.[1]?.headers as Headers;
    expect(loginHeaders.get("X-CSRFToken")).toBe("csrf-token-1");
  });

  it("normalizes current user snake_case payload to camelCase", async () => {
    mockFetch(backendUser);

    await expect(authService.currentUser()).resolves.toEqual({
      id: "user-1",
      username: "admin",
      email: "admin@tcms.test",
      fullName: "Admin User",
      forcePasswordChange: false,
      roles: [{ id: "role-1", code: "branch_admin", name: "Branch Admin", isReadOnly: false }],
      permissions: [{ id: "perm-1", code: "students.view", name: "View students", module: "students", isReadOnly: true }],
      branchAssignments: [{ id: "branch-assignment-1", organizationId: "org-1", branchId: "branch-1", isPrimary: true }],
    });
  });

  it("normalizes authenticated session user", async () => {
    mockFetch({ authenticated: true, user: backendUser });

    await expect(authService.checkSession()).resolves.toMatchObject({
      authenticated: true,
      user: {
        fullName: "Admin User",
        roles: [{ code: "branch_admin", name: "Branch Admin" }],
        branchAssignments: [{ branchId: "branch-1", isPrimary: true }],
      },
    });
  });

  it("calls password reset endpoints with backend field names", async () => {
    const fetchMock = mockFetch({});

    await authService.requestPasswordReset({ email: "admin@tcms.test" });
    await authService.confirmPasswordReset({ token: "reset-token", newPassword: "StrongPass123!" });

    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/api/v1/auth/password-reset/request/",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ email: "admin@tcms.test" }),
      }),
    );
    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/api/v1/auth/password-reset/confirm/",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ token: "reset-token", new_password: "StrongPass123!" }),
      }),
    );
  });
});
