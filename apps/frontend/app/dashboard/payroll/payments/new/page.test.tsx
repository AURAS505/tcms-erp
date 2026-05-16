import React from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import NewTeacherPaymentPage from "@/app/dashboard/payroll/payments/new/page";
import { useAuth } from "@/hooks/useAuth";
import { listAcademicYears, listBranches, listOrganizations } from "@/lib/lookups";
import { createDraftTeacherPayment } from "@/lib/payroll";
import { listTeachers } from "@/lib/teachers";

const push = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push }),
}));

vi.mock("@/hooks/useAuth", () => ({
  useAuth: vi.fn(),
}));

vi.mock("@/lib/lookups", () => ({
  listAcademicYears: vi.fn(),
  listBranches: vi.fn(),
  listOrganizations: vi.fn(),
}));

vi.mock("@/lib/payroll", () => ({
  createDraftTeacherPayment: vi.fn(),
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
      <NewTeacherPaymentPage />
    </QueryClientProvider>,
  );
}

async function fillRequiredFields() {
  await screen.findByRole("option", { name: "TCMS" });
  fireEvent.change(screen.getByLabelText(/organization/i), { target: { value: "org-1" } });
  fireEvent.change(screen.getByLabelText(/^branch$/i), { target: { value: "branch-1" } });
  fireEvent.change(screen.getByLabelText(/academic year/i), { target: { value: "year-1" } });
  fireEvent.change(screen.getByLabelText(/^teacher$/i), { target: { value: "teacher-1" } });
  fireEvent.change(screen.getByLabelText(/payment date/i), { target: { value: "2026-04-15" } });
  fireEvent.change(screen.getByLabelText(/^amount$/i), { target: { value: "500.00" } });
  fireEvent.change(screen.getByLabelText(/teacher earning id/i), { target: { value: "earning-1" } });
  fireEvent.change(screen.getByLabelText(/allocation amount/i), { target: { value: "500.00" } });
}

describe("NewTeacherPaymentPage", () => {
  beforeEach(() => {
    push.mockReset();
    mockRole("accountant");
    vi.mocked(createDraftTeacherPayment).mockReset();
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

  it("renders teacher payment draft form", async () => {
    renderPage();

    expect(await screen.findByRole("heading", { name: "New Teacher Payment" })).toBeInTheDocument();
    expect(screen.getByLabelText(/payment date/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/teacher earning id/i)).toBeInTheDocument();
  });

  it("submits draft payment payload and redirects", async () => {
    vi.mocked(createDraftTeacherPayment).mockResolvedValue({
      id: "payment-1",
      organization: "org-1",
      branch: "branch-1",
      academic_year: "year-1",
      academic_period: null,
      payment_batch: null,
      teacher: "teacher-1",
      voucher_number: null,
      draft_voucher_number: "TDV-000001",
      payment_date_ad: "2026-04-15",
      payment_date_bs: "",
      payment_method: "cash",
      amount: "500.00",
      deduction_amount: "0.00",
      net_paid_amount: "500.00",
      reference_number: "",
      acknowledgement_file_path: "",
      status: "draft",
      created_by: null,
      approved_by: null,
      approved_at: null,
      posted_at: null,
      voided_by: null,
      voided_at: null,
      void_reason: "",
      notes: "",
      created_at: "2026-01-01T00:00:00Z",
      updated_at: "2026-01-01T00:00:00Z",
    });
    renderPage();

    await fillRequiredFields();
    fireEvent.click(screen.getByRole("button", { name: /create draft payment/i }));

    await waitFor(() => expect(createDraftTeacherPayment).toHaveBeenCalled());
    expect(vi.mocked(createDraftTeacherPayment).mock.calls[0][0]).toEqual(
      expect.objectContaining({
        organization: "org-1",
        branch: "branch-1",
        academic_year: "year-1",
        teacher: "teacher-1",
        payment_date_ad: "2026-04-15",
        amount: "500.00",
        allocations: [{ teacher_earning: "earning-1", amount_allocated: "500.00" }],
      }),
    );
    await waitFor(() => expect(push).toHaveBeenCalledWith("/dashboard/payroll/payments/payment-1"));
  });

  it("disables mutation for teacher role", async () => {
    mockRole("teacher");
    renderPage();

    expect(await screen.findByText(/cannot create teacher payments/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /create draft payment/i })).toBeDisabled();
  });
});
