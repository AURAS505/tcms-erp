import React from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import NewTeacherPaymentPage from "@/app/dashboard/payroll/payments/new/page";
import { useAuth } from "@/hooks/useAuth";
import { listAcademicYears, listBranches, listOrganizations } from "@/lib/lookups";
import { createDraftTeacherPayment, listTeacherEarnings } from "@/lib/payroll";
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
  listTeacherEarnings: vi.fn(),
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

async function fillRequiredFields(paymentAmount = "750.00") {
  await screen.findByRole("option", { name: "TCMS" });
  fireEvent.change(screen.getByLabelText(/organization/i), { target: { value: "org-1" } });
  fireEvent.change(screen.getByLabelText(/^branch$/i), { target: { value: "branch-1" } });
  fireEvent.change(screen.getByLabelText(/academic year/i), { target: { value: "year-1" } });
  fireEvent.change(screen.getByLabelText(/^teacher$/i), { target: { value: "teacher-1" } });
  fireEvent.change(screen.getByLabelText(/payment date/i), { target: { value: "2026-04-15" } });
  fireEvent.change(screen.getByLabelText(/^amount$/i), { target: { value: paymentAmount } });
  await screen.findByRole("option", { name: /Baishakh 2083 - 2026-04-10 - balance 1000.00/i });
}

async function selectFirstAllocation(amount = "500.00") {
  fireEvent.change(screen.getByLabelText(/earning 1/i), { target: { value: "earning-1" } });
  await waitFor(() => expect(screen.getByLabelText(/allocation amount 1/i)).not.toBeDisabled());
  fireEvent.change(screen.getByLabelText(/allocation amount 1/i), { target: { value: amount } });
}

async function addSecondAllocation(amount = "250.00") {
  fireEvent.click(screen.getByRole("button", { name: /add allocation/i }));
  await screen.findByLabelText(/earning 2/i);
  fireEvent.change(screen.getByLabelText(/earning 2/i), { target: { value: "earning-2" } });
  await waitFor(() => expect(screen.getByLabelText(/allocation amount 2/i)).not.toBeDisabled());
  fireEvent.change(screen.getByLabelText(/allocation amount 2/i), { target: { value: amount } });
}

describe("NewTeacherPaymentPage", () => {
  beforeEach(() => {
    push.mockReset();
    mockRole("accountant");
    vi.mocked(createDraftTeacherPayment).mockReset();
    vi.mocked(listTeacherEarnings).mockResolvedValue({
      data: [
        {
          id: "earning-1",
          organization: "org-1",
          branch: "branch-1",
          academic_year: "year-1",
          academic_period: null,
          teacher: "teacher-1",
          student: null,
          class_room: null,
          class_enrollment: null,
          student_payment: null,
          earning_source: "manual_adjustment",
          earning_date_ad: "2026-04-10",
          earning_date_bs: "",
          period_label: "Baishakh 2083",
          gross_amount: "1000.00",
          deduction_amount: "0.00",
          net_amount: "1000.00",
          paid_amount: "0.00",
          balance_amount: "1000.00",
          status: "posted",
          created_by: null,
          approved_by: null,
          approved_at: null,
          posted_at: "2026-04-10T00:00:00Z",
          notes: "",
          created_at: "2026-01-01T00:00:00Z",
          updated_at: "2026-01-01T00:00:00Z",
        },
        {
          id: "earning-2",
          organization: "org-1",
          branch: "branch-1",
          academic_year: "year-1",
          academic_period: null,
          teacher: "teacher-1",
          student: null,
          class_room: null,
          class_enrollment: null,
          student_payment: null,
          earning_source: "manual_adjustment",
          earning_date_ad: "2026-05-10",
          earning_date_bs: "",
          period_label: "Jestha 2083",
          gross_amount: "600.00",
          deduction_amount: "0.00",
          net_amount: "600.00",
          paid_amount: "100.00",
          balance_amount: "500.00",
          status: "partial",
          created_by: null,
          approved_by: null,
          approved_at: null,
          posted_at: "2026-05-10T00:00:00Z",
          notes: "",
          created_at: "2026-01-01T00:00:00Z",
          updated_at: "2026-01-01T00:00:00Z",
        },
      ],
      pagination: { count: 2, page: 1, page_size: 25, next: null, previous: null },
    });
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
    expect(screen.queryByLabelText(/teacher earning id/i)).not.toBeInTheDocument();
    expect(screen.getByText(/select a teacher to load open earnings/i)).toBeInTheDocument();
  });

  it("loads open earnings after teacher selection", async () => {
    renderPage();

    await screen.findByRole("option", { name: "TCMS" });
    fireEvent.change(screen.getByLabelText(/organization/i), { target: { value: "org-1" } });
    fireEvent.change(screen.getByLabelText(/^branch$/i), { target: { value: "branch-1" } });
    fireEvent.change(screen.getByLabelText(/academic year/i), { target: { value: "year-1" } });
    fireEvent.change(screen.getByLabelText(/^teacher$/i), { target: { value: "teacher-1" } });

    await waitFor(() => expect(listTeacherEarnings).toHaveBeenCalled());
    expect(listTeacherEarnings).toHaveBeenCalledWith(
      expect.objectContaining({
        organization: "org-1",
        branch: "branch-1",
        academic_year: "year-1",
        teacher: "teacher-1",
        open_only: true,
      }),
    );
    expect(await screen.findByText("Baishakh 2083")).toBeInTheDocument();
    expect(screen.getByText("Jestha 2083")).toBeInTheDocument();
  });

  it("adds and removes allocation rows", async () => {
    renderPage();

    await fillRequiredFields();
    await selectFirstAllocation("250.00");
    fireEvent.click(screen.getByRole("button", { name: /add allocation/i }));

    expect(await screen.findByLabelText(/earning 2/i)).toBeInTheDocument();

    const removeButtons = screen.getAllByRole("button", { name: /remove/i });
    fireEvent.click(removeButtons[1]);

    await waitFor(() => expect(screen.queryByLabelText(/earning 2/i)).not.toBeInTheDocument());
  });

  it("flags duplicate selected earnings", async () => {
    renderPage();

    await fillRequiredFields();
    await selectFirstAllocation("250.00");
    fireEvent.click(screen.getByRole("button", { name: /add allocation/i }));
    fireEvent.change(await screen.findByLabelText(/earning 2/i), { target: { value: "earning-1" } });
    fireEvent.change(screen.getByLabelText(/allocation amount 2/i), { target: { value: "100.00" } });

    expect((await screen.findAllByText(/duplicates another allocation/i)).length).toBeGreaterThan(0);
    expect(screen.getByRole("button", { name: /create draft payment/i })).toBeDisabled();
  });

  it("shows allocation total and blocks totals above payment amount", async () => {
    renderPage();

    await fillRequiredFields("500.00");
    await selectFirstAllocation("400.00");
    await addSecondAllocation("200.00");

    expect(screen.getByText(/allocation total:/i)).toBeInTheDocument();
    expect(screen.getByText(/unallocated amount:/i)).toBeInTheDocument();
    expect(screen.getByText(/allocation total cannot exceed payment amount/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /create draft payment/i })).toBeDisabled();
  });

  it("blocks allocation amount above selected earning balance", async () => {
    renderPage();

    await fillRequiredFields("1500.00");
    await selectFirstAllocation("1200.00");

    expect(await screen.findByText(/allocation row 1 amount cannot exceed the selected earning balance/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /create draft payment/i })).toBeDisabled();
  });

  it("shows empty state when teacher has no open earnings", async () => {
    vi.mocked(listTeacherEarnings).mockResolvedValue({
      data: [],
      pagination: { count: 0, page: 1, page_size: 25, next: null, previous: null },
    });
    renderPage();

    await screen.findByRole("option", { name: "TCMS" });
    fireEvent.change(screen.getByLabelText(/^teacher$/i), { target: { value: "teacher-1" } });

    expect(await screen.findByText(/no unpaid posted teacher earnings were found/i)).toBeInTheDocument();
  });

  it("creates draft payment with multiple allocations and redirects", async () => {
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
      amount: "750.00",
      deduction_amount: "0.00",
      net_paid_amount: "750.00",
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

    await fillRequiredFields("750.00");
    await selectFirstAllocation("500.00");
    await addSecondAllocation("250.00");
    fireEvent.click(screen.getByRole("button", { name: /create draft payment/i }));

    await waitFor(() => expect(createDraftTeacherPayment).toHaveBeenCalled());
    expect(vi.mocked(createDraftTeacherPayment).mock.calls[0][0]).toEqual(
      expect.objectContaining({
        organization: "org-1",
        branch: "branch-1",
        academic_year: "year-1",
        teacher: "teacher-1",
        payment_date_ad: "2026-04-15",
        amount: "750.00",
        allocations: [
          { teacher_earning: "earning-1", amount_allocated: "500.00" },
          { teacher_earning: "earning-2", amount_allocated: "250.00" },
        ],
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
