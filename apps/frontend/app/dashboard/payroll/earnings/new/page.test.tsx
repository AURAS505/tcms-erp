import React from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import NewTeacherEarningPage from "@/app/dashboard/payroll/earnings/new/page";
import { useAuth } from "@/hooks/useAuth";
import { listAcademicPeriods, listAcademicYears, listBranches, listOrganizations } from "@/lib/lookups";
import { createManualTeacherEarning } from "@/lib/payroll";
import { listTeachers } from "@/lib/teachers";

const push = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push }),
}));

vi.mock("@/hooks/useAuth", () => ({
  useAuth: vi.fn(),
}));

vi.mock("@/lib/lookups", () => ({
  listAcademicPeriods: vi.fn(),
  listAcademicYears: vi.fn(),
  listBranches: vi.fn(),
  listOrganizations: vi.fn(),
}));

vi.mock("@/lib/payroll", () => ({
  createManualTeacherEarning: vi.fn(),
}));

vi.mock("@/lib/teachers", () => ({
  listTeachers: vi.fn(),
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
      <NewTeacherEarningPage />
    </QueryClientProvider>,
  );
}

async function fillRequiredFields() {
  await screen.findByRole("option", { name: "TCMS" });
  fireEvent.change(screen.getByLabelText(/organization/i), { target: { value: "org-1" } });
  fireEvent.change(screen.getByLabelText(/^branch$/i), { target: { value: "branch-1" } });
  fireEvent.change(screen.getByLabelText(/academic year/i), { target: { value: "year-1" } });
  fireEvent.change(screen.getByLabelText(/academic period/i), { target: { value: "period-1" } });
  fireEvent.change(screen.getByLabelText(/teacher/i), { target: { value: "teacher-1" } });
  fireEvent.change(screen.getByLabelText(/earning date/i), { target: { value: "2026-04-15" } });
  fireEvent.change(screen.getByLabelText(/gross amount/i), { target: { value: "1000.00" } });
  fireEvent.change(screen.getByLabelText(/deduction amount/i), { target: { value: "100.00" } });
}

describe("NewTeacherEarningPage", () => {
  beforeEach(() => {
    push.mockReset();
    mockRole("accountant");
    vi.mocked(createManualTeacherEarning).mockReset();
    vi.mocked(listOrganizations).mockResolvedValue({
      data: [{ id: "org-1", display_name: "TCMS", legal_name: "TCMS Pvt Ltd", is_active: true }],
      pagination: { count: 1, page: 1, page_size: 25, next: null, previous: null },
    });
    vi.mocked(listBranches).mockResolvedValue({
      data: [{ id: "branch-1", organization: "org-1", code: "MAIN", name: "Main Branch", is_active: true }],
      pagination: { count: 1, page: 1, page_size: 25, next: null, previous: null },
    });
    vi.mocked(listAcademicYears).mockResolvedValue({
      data: [{ id: "year-1", organization: "org-1", name: "2083", ad_start_date: "2026-04-14", ad_end_date: "2027-04-13", status: "active", is_active: true }],
      pagination: { count: 1, page: 1, page_size: 25, next: null, previous: null },
    });
    vi.mocked(listAcademicPeriods).mockResolvedValue({
      data: [{ id: "period-1", organization: "org-1", academic_year: "year-1", name: "Baishakh 2083", ad_start_date: "2026-04-14", ad_end_date: "2026-05-14", status: "active", is_active: true }],
      pagination: { count: 1, page: 1, page_size: 25, next: null, previous: null },
    });
    vi.mocked(listTeachers).mockResolvedValue({
      data: [
        {
          id: "teacher-1",
          organization: "org-1",
          branch: "branch-1",
          user: null,
          employee_number: "T-001",
          full_name: "Ram Sir",
          preferred_name: "",
          gender: "",
          date_of_birth_ad: null,
          date_of_birth_bs: "",
          phone: "",
          alternate_phone: "",
          email: "",
          address: "",
          qualification: "",
          specialization: "",
          experience_summary: "",
          joining_date_ad: null,
          joining_date_bs: "",
          photo_path: "",
          status: "active",
          notes: "",
          created_at: "2026-01-01T00:00:00Z",
          updated_at: "2026-01-01T00:00:00Z",
        },
      ],
      pagination: { count: 1, page: 1, page_size: 25, next: null, previous: null },
    });
  });

  it("renders manual earning form", async () => {
    renderPage();

    expect(await screen.findByRole("heading", { name: "New Teacher Earning" })).toBeInTheDocument();
    expect(screen.getByLabelText(/earning date/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/gross amount/i)).toBeInTheDocument();
  });

  it("submits manual earning payload and redirects", async () => {
    vi.mocked(createManualTeacherEarning).mockResolvedValue({
      id: "earning-1",
      organization: "org-1",
      branch: "branch-1",
      academic_year: "year-1",
      academic_period: "period-1",
      teacher: "teacher-1",
      student: null,
      class_room: null,
      class_enrollment: null,
      student_payment: null,
      earning_source: "manual_adjustment",
      earning_date_ad: "2026-04-15",
      earning_date_bs: "",
      period_label: "",
      gross_amount: "1000.00",
      deduction_amount: "100.00",
      net_amount: "900.00",
      paid_amount: "0.00",
      balance_amount: "900.00",
      status: "draft",
      created_by: null,
      approved_by: null,
      approved_at: null,
      posted_at: null,
      notes: "",
      created_at: "2026-01-01T00:00:00Z",
      updated_at: "2026-01-01T00:00:00Z",
    });
    renderPage();

    await fillRequiredFields();
    fireEvent.click(screen.getByRole("button", { name: /create manual earning/i }));

    await waitFor(() => expect(createManualTeacherEarning).toHaveBeenCalled());
    expect(vi.mocked(createManualTeacherEarning).mock.calls[0][0]).toEqual(
      expect.objectContaining({
        organization: "org-1",
        branch: "branch-1",
        academic_year: "year-1",
        academic_period: "period-1",
        teacher: "teacher-1",
        earning_date_ad: "2026-04-15",
        gross_amount: "1000.00",
        deduction_amount: "100.00",
      }),
    );
    await waitFor(() => expect(push).toHaveBeenCalledWith("/dashboard/payroll/earnings/earning-1"));
  });

  it("disables mutation for receptionist", async () => {
    mockRole("receptionist");
    renderPage();

    expect(await screen.findByText(/cannot create teacher earnings/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /create manual earning/i })).toBeDisabled();
  });
});
