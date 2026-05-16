import React from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import TeacherEarningsPage from "@/app/dashboard/payroll/earnings/page";
import { listTeacherEarnings } from "@/lib/payroll";

vi.mock("@/lib/payroll", () => ({
  listTeacherEarnings: vi.fn(),
}));

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <TeacherEarningsPage />
    </QueryClientProvider>,
  );
}

describe("TeacherEarningsPage", () => {
  beforeEach(() => {
    vi.mocked(listTeacherEarnings).mockReset();
  });

  it("renders loading state", () => {
    vi.mocked(listTeacherEarnings).mockReturnValue(new Promise(() => undefined));
    renderPage();

    expect(screen.getByRole("status")).toHaveTextContent("Loading teacher earnings...");
  });

  it("renders empty state", async () => {
    vi.mocked(listTeacherEarnings).mockResolvedValue({
      data: [],
      pagination: { count: 0, page: 1, page_size: 25, next: null, previous: null },
    });
    renderPage();

    expect(await screen.findByText("No teacher earnings found")).toBeInTheDocument();
  });

  it("renders data state", async () => {
    vi.mocked(listTeacherEarnings).mockResolvedValue({
      data: [
        {
          id: "earning-1",
          organization: "org-1",
          branch: "branch-1",
          academic_year: "year-1",
          academic_period: null,
          teacher: "teacher-1",
          student: "student-1",
          class_room: "class-1",
          class_enrollment: "enrollment-1",
          student_payment: "student-payment-1",
          earning_source: "student_payment",
          earning_date_ad: "2026-04-15",
          earning_date_bs: "",
          period_label: "Baisakh 2083",
          gross_amount: "5000.00",
          deduction_amount: "0.00",
          net_amount: "5000.00",
          paid_amount: "0.00",
          balance_amount: "5000.00",
          status: "approved",
          created_by: null,
          approved_by: null,
          approved_at: null,
          posted_at: null,
          notes: "",
          created_at: "2026-01-01T00:00:00Z",
          updated_at: "2026-01-01T00:00:00Z",
        },
      ],
      pagination: { count: 1, page: 1, page_size: 25, next: null, previous: null },
    });
    renderPage();

    expect(await screen.findByRole("link", { name: "Baisakh 2083" })).toHaveAttribute(
      "href",
      "/dashboard/payroll/earnings/earning-1",
    );
    expect(screen.getByText("Student Payment")).toBeInTheDocument();
  });
});
