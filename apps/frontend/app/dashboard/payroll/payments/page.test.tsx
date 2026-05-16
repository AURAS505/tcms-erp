import React from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import TeacherPaymentsPage from "@/app/dashboard/payroll/payments/page";
import { listTeacherPayments } from "@/lib/payroll";

vi.mock("@/lib/payroll", () => ({
  listTeacherPayments: vi.fn(),
}));

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <TeacherPaymentsPage />
    </QueryClientProvider>,
  );
}

describe("TeacherPaymentsPage", () => {
  beforeEach(() => {
    vi.mocked(listTeacherPayments).mockReset();
  });

  it("renders loading state", () => {
    vi.mocked(listTeacherPayments).mockReturnValue(new Promise(() => undefined));
    renderPage();

    expect(screen.getByRole("status")).toHaveTextContent("Loading teacher payments...");
  });

  it("renders empty state", async () => {
    vi.mocked(listTeacherPayments).mockResolvedValue({
      data: [],
      pagination: { count: 0, page: 1, page_size: 25, next: null, previous: null },
    });
    renderPage();

    expect(await screen.findByText("No teacher payments found")).toBeInTheDocument();
  });

  it("renders data state", async () => {
    vi.mocked(listTeacherPayments).mockResolvedValue({
      data: [
        {
          id: "payment-1",
          organization: "org-1",
          branch: "branch-1",
          academic_year: "year-1",
          academic_period: null,
          payment_batch: "batch-1",
          teacher: "teacher-1",
          voucher_number: "TPV-001",
          draft_voucher_number: null,
          payment_date_ad: "2026-04-15",
          payment_date_bs: "",
          payment_method: "cash",
          amount: "5000.00",
          deduction_amount: "0.00",
          net_paid_amount: "5000.00",
          reference_number: "",
          acknowledgement_file_path: "",
          status: "posted",
          created_by: null,
          approved_by: null,
          approved_at: null,
          posted_at: "2026-04-15T00:00:00Z",
          voided_by: null,
          voided_at: null,
          void_reason: "",
          notes: "",
          created_at: "2026-01-01T00:00:00Z",
          updated_at: "2026-01-01T00:00:00Z",
        },
      ],
      pagination: { count: 1, page: 1, page_size: 25, next: null, previous: null },
    });
    renderPage();

    expect(await screen.findByRole("link", { name: "TPV-001" })).toHaveAttribute(
      "href",
      "/dashboard/payroll/payments/payment-1",
    );
    expect(screen.getByText("Posted")).toBeInTheDocument();
  });
});
