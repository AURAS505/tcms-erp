import React from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import TeacherPaymentBatchesPage from "@/app/dashboard/payroll/payment-batches/page";
import { listTeacherPaymentBatches } from "@/lib/payroll";

vi.mock("@/lib/payroll", () => ({
  listTeacherPaymentBatches: vi.fn(),
}));

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <TeacherPaymentBatchesPage />
    </QueryClientProvider>,
  );
}

describe("TeacherPaymentBatchesPage", () => {
  beforeEach(() => {
    vi.mocked(listTeacherPaymentBatches).mockReset();
  });

  it("renders loading state", () => {
    vi.mocked(listTeacherPaymentBatches).mockReturnValue(new Promise(() => undefined));
    renderPage();

    expect(screen.getByRole("status")).toHaveTextContent("Loading payment batches...");
  });

  it("renders empty state", async () => {
    vi.mocked(listTeacherPaymentBatches).mockResolvedValue({
      data: [],
      pagination: { count: 0, page: 1, page_size: 25, next: null, previous: null },
    });
    renderPage();

    expect(await screen.findByText("No payment batches found")).toBeInTheDocument();
  });

  it("renders data state", async () => {
    vi.mocked(listTeacherPaymentBatches).mockResolvedValue({
      data: [
        {
          id: "batch-1",
          organization: "org-1",
          branch: "branch-1",
          academic_year: "year-1",
          academic_period: null,
          batch_number: "TPB-001",
          batch_date_ad: "2026-04-15",
          batch_date_bs: "",
          description: "April teacher payout",
          total_amount: "5000.00",
          status: "draft",
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

    expect(await screen.findByRole("link", { name: "TPB-001" })).toHaveAttribute(
      "href",
      "/dashboard/payroll/payment-batches/batch-1",
    );
    expect(screen.getByText("Draft")).toBeInTheDocument();
  });
});
