import React from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import NewAcademicRolloverPage from "@/app/dashboard/academic-rollovers/new/page";
import { useAuth } from "@/hooks/useAuth";
import { listAcademicYears, prepareAcademicRollover } from "@/lib/academic";
import { listOrganizations } from "@/lib/lookups";

const push = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push }),
}));

vi.mock("@/hooks/useAuth", () => ({
  useAuth: vi.fn(),
}));

vi.mock("@/lib/academic", () => ({
  listAcademicYears: vi.fn(),
  prepareAcademicRollover: vi.fn(),
}));

vi.mock("@/lib/lookups", () => ({
  listOrganizations: vi.fn(),
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
      <NewAcademicRolloverPage />
    </QueryClientProvider>,
  );
}

describe("NewAcademicRolloverPage", () => {
  beforeEach(() => {
    push.mockReset();
    mockRole("accountant");
    vi.mocked(prepareAcademicRollover).mockReset();
    vi.mocked(listOrganizations).mockResolvedValue({
      data: [{ id: "org-1", display_name: "TCMS", legal_name: "TCMS Pvt Ltd", is_active: true }],
      pagination: { count: 1, page: 1, page_size: 25, next: null, previous: null },
    });
    vi.mocked(listAcademicYears).mockResolvedValue({
      data: [
        {
          id: "year-1",
          organization: "org-1",
          name: "2083/2084",
          bs_start_year: 2083,
          bs_end_year: 2084,
          bs_start_date: "2083-01-01",
          bs_end_date: "2083-12-30",
          ad_start_date: "2026-04-14",
          ad_end_date: "2027-04-13",
          status: "active",
          is_active: true,
          notes: "",
          created_at: "",
          updated_at: "",
        },
      ],
      pagination: { count: 1, page: 1, page_size: 25, next: null, previous: null },
    });
  });

  it("renders rollover prepare form", async () => {
    renderPage();

    expect(await screen.findByRole("heading", { name: "New Academic Rollover" })).toBeInTheDocument();
    expect(screen.getByLabelText(/outgoing academic year/i)).toBeInTheDocument();
  });

  it("submits prepare payload and redirects", async () => {
    vi.mocked(prepareAcademicRollover).mockResolvedValue({
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
    });
    renderPage();

    await screen.findByRole("option", { name: "TCMS" });
    fireEvent.change(screen.getByLabelText(/organization/i), { target: { value: "org-1" } });
    fireEvent.change(screen.getByLabelText(/outgoing academic year/i), { target: { value: "year-1" } });
    fireEvent.click(screen.getByRole("button", { name: /prepare rollover/i }));

    await waitFor(() => expect(prepareAcademicRollover).toHaveBeenCalled());
    expect(vi.mocked(prepareAcademicRollover).mock.calls[0][0]).toEqual(
      expect.objectContaining({ organization: "org-1", from_academic_year: "year-1" }),
    );
    await waitFor(() => expect(push).toHaveBeenCalledWith("/dashboard/academic-rollovers/rollover-1"));
  });

  it("disables prepare for receptionist", async () => {
    mockRole("receptionist");
    renderPage();

    expect(await screen.findByText(/cannot prepare them/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /prepare rollover/i })).toBeDisabled();
  });
});
