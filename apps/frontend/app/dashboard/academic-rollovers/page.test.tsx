import React from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import AcademicRolloversPage from "@/app/dashboard/academic-rollovers/page";
import { useAuth } from "@/hooks/useAuth";
import { listAcademicRollovers } from "@/lib/academic";

vi.mock("@/hooks/useAuth", () => ({
  useAuth: vi.fn(),
}));

vi.mock("@/lib/academic", () => ({
  listAcademicRollovers: vi.fn(),
}));

function mockRole(role: string) {
  vi.mocked(useAuth).mockReturnValue({
    branchAssignments: [],
    error: null,
    hasPermission: vi.fn(() => false),
    hasRole: vi.fn((candidate) => candidate === role),
    isAuthenticated: true,
    isLoading: false,
    login: vi.fn(),
    logout: vi.fn(),
    permissions: [],
    refreshSession: vi.fn(),
    user: null,
  });
}

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <AcademicRolloversPage />
    </QueryClientProvider>,
  );
}

describe("AcademicRolloversPage", () => {
  beforeEach(() => {
    mockRole("super_admin");
    vi.mocked(listAcademicRollovers).mockReset();
    vi.mocked(listAcademicRollovers).mockResolvedValue({
      data: [
        {
          id: "rollover-1",
          organization: "org-1",
          from_academic_year: "year-1",
          to_academic_year: null,
          status: "draft",
          trial_balance_validated: false,
          revenue_expense_closing_completed: false,
          opening_balances_posted: false,
          executed_by: null,
          executed_at: null,
          notes: "",
          created_at: "",
          updated_at: "",
        },
      ],
      pagination: { count: 1, page: 1, page_size: 25, next: null, previous: null },
    });
  });

  it("renders rollover list and new action for super admin", async () => {
    renderPage();

    expect(await screen.findByRole("link", { name: "rollover-1" })).toHaveAttribute("href", "/dashboard/academic-rollovers/rollover-1");
    expect(screen.getByRole("link", { name: /new rollover/i })).toHaveAttribute("href", "/dashboard/academic-rollovers/new");
  });

  it.each(["receptionist", "teacher", "auditor"])("hides mutation action for %s", async (role) => {
    mockRole(role);
    renderPage();

    expect(await screen.findByRole("link", { name: "rollover-1" })).toBeInTheDocument();
    expect(screen.queryByRole("link", { name: /new rollover/i })).not.toBeInTheDocument();
  });
});
