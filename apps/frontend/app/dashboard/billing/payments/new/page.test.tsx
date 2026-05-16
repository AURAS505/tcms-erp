import React from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import NewPaymentPage from "@/app/dashboard/billing/payments/new/page";
import { createDraftStudentPayment } from "@/lib/billing";
import { listAcademicYears, listBranches, listOrganizations } from "@/lib/lookups";
import { listStudents } from "@/lib/students";

const push = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push }),
}));

vi.mock("@/lib/billing", () => ({
  createDraftStudentPayment: vi.fn(),
}));

vi.mock("@/lib/lookups", () => ({
  listOrganizations: vi.fn(),
  listBranches: vi.fn(),
  listAcademicYears: vi.fn(),
}));

vi.mock("@/lib/students", () => ({
  listStudents: vi.fn(),
}));

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <NewPaymentPage />
    </QueryClientProvider>,
  );
}

describe("NewPaymentPage", () => {
  beforeEach(() => {
    push.mockReset();
    vi.mocked(createDraftStudentPayment).mockReset();
    vi.mocked(listOrganizations).mockResolvedValue({
      data: [{ id: "org-1", display_name: "TCMS", legal_name: "TCMS Pvt Ltd", is_active: true }],
      pagination: { count: 1, page: 1, page_size: 25, next: null, previous: null },
    });
    vi.mocked(listBranches).mockResolvedValue({
      data: [{ id: "branch-1", organization: "org-1", code: "MAIN", name: "Main Branch", is_active: true }],
      pagination: { count: 1, page: 1, page_size: 25, next: null, previous: null },
    });
    vi.mocked(listAcademicYears).mockResolvedValue({
      data: [
        {
          id: "year-1",
          organization: "org-1",
          name: "2083",
          ad_start_date: "2026-04-14",
          ad_end_date: "2027-04-13",
          status: "active",
          is_active: true,
        },
      ],
      pagination: { count: 1, page: 1, page_size: 25, next: null, previous: null },
    });
    vi.mocked(listStudents).mockResolvedValue({
      data: [
        {
          id: "student-1",
          admission_number: "ADM-001",
          full_name: "Sita Sharma",
          preferred_name: "",
          gender: "",
          date_of_birth_ad: null,
          date_of_birth_bs: "",
          phone: "",
          email: "",
          permanent_address: "",
          temporary_address: "",
          school_college_name: "",
          current_grade_class: "",
          status: "active",
          admission_date_ad: null,
          admission_date_bs: "",
          notes: "",
          created_at: "2026-01-01T00:00:00Z",
          updated_at: "2026-01-01T00:00:00Z",
        },
      ],
      pagination: { count: 1, page: 1, page_size: 25, next: null, previous: null },
    });
  });

  it("renders payment draft form", async () => {
    renderPage();

    expect(await screen.findByRole("heading", { name: "New Payment" })).toBeInTheDocument();
    expect(screen.getByLabelText(/payment date/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/^amount$/i)).toBeInTheDocument();
  });

  it("creates draft payment and redirects to detail page", async () => {
    vi.mocked(createDraftStudentPayment).mockResolvedValue({
      id: "payment-1",
      organization: "org-1",
      branch: "branch-1",
      academic_year: "year-1",
      student: "student-1",
      receipt_number: null,
      draft_receipt_number: "DR-000001",
      payment_date_ad: "2026-04-15",
      payment_date_bs: "",
      payment_method: "cash",
      amount: "500.00",
      discount_amount: "0.00",
      fine_amount: "0.00",
      net_received_amount: "500.00",
      reference_number: "",
      file_path: "",
      is_advance_payment: true,
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

    await screen.findByRole("option", { name: "TCMS" });
    await screen.findByRole("option", { name: "Main Branch" });
    await screen.findByRole("option", { name: "2083" });
    await screen.findByRole("option", { name: "Sita Sharma" });
    fireEvent.change(await screen.findByLabelText(/organization/i), { target: { value: "org-1" } });
    fireEvent.change(screen.getByLabelText(/branch/i), { target: { value: "branch-1" } });
    fireEvent.change(screen.getByLabelText(/academic year/i), { target: { value: "year-1" } });
    fireEvent.change(screen.getByLabelText(/student/i), { target: { value: "student-1" } });
    fireEvent.change(screen.getByLabelText(/payment date/i), { target: { value: "2026-04-15" } });
    fireEvent.change(screen.getByLabelText(/^amount$/i), { target: { value: "500.00" } });
    fireEvent.click(screen.getByLabelText(/advance payment/i));
    fireEvent.click(screen.getByRole("button", { name: /create draft/i }));

    await waitFor(() => expect(createDraftStudentPayment).toHaveBeenCalled());
    expect(vi.mocked(createDraftStudentPayment).mock.calls[0][0]).toEqual(
      expect.objectContaining({
        amount: "500.00",
        is_advance_payment: true,
        organization: "org-1",
        student: "student-1",
      }),
    );
    await waitFor(() => expect(push).toHaveBeenCalledWith("/dashboard/billing/payments/payment-1"));
  });
});
