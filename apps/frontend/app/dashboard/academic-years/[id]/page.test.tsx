import React from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import AcademicYearDetailPage from "@/app/dashboard/academic-years/[id]/page";
import { useAuth } from "@/hooks/useAuth";
import { getAcademicYear, hardCloseAcademicYear, softCloseAcademicYear } from "@/lib/academic";

vi.mock("@/hooks/useAuth", () => ({ useAuth: vi.fn() }));
vi.mock("@/lib/academic", () => ({
  getAcademicYear: vi.fn(),
  hardCloseAcademicYear: vi.fn(),
  softCloseAcademicYear: vi.fn(),
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
      <AcademicYearDetailPage params={{ id: "year-1" }} />
    </QueryClientProvider>,
  );
}

describe("AcademicYearDetailPage", () => {
  beforeEach(() => {
    mockRole("accountant");
    vi.mocked(hardCloseAcademicYear).mockReset();
    vi.mocked(softCloseAcademicYear).mockReset();
    vi.mocked(getAcademicYear).mockResolvedValue({
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
    });
  });

  it("hides hard close from accountant", async () => {
    renderPage();

    expect(await screen.findByRole("button", { name: /soft close/i })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /hard close/i })).not.toBeInTheDocument();
  });

  it("shows hard close for institute owner", async () => {
    mockRole("institute_owner");
    renderPage();

    expect(await screen.findByRole("button", { name: /hard close/i })).toBeInTheDocument();
  });
});
