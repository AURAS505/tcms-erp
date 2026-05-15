import React from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import FeeDuesPage from "@/app/dashboard/billing/dues/page";
import { listFeeDues } from "@/lib/billing";

vi.mock("@/lib/billing", () => ({
  listFeeDues: vi.fn(),
}));

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <FeeDuesPage />
    </QueryClientProvider>,
  );
}

describe("FeeDuesPage", () => {
  beforeEach(() => {
    vi.mocked(listFeeDues).mockReset();
  });

  it("renders loading state", () => {
    vi.mocked(listFeeDues).mockReturnValue(new Promise(() => undefined));
    renderPage();

    expect(screen.getByRole("status")).toHaveTextContent("Loading fee dues...");
  });

  it("renders empty state", async () => {
    vi.mocked(listFeeDues).mockResolvedValue({
      data: [],
      pagination: { count: 0, page: 1, page_size: 25, next: null, previous: null },
    });
    renderPage();

    expect(await screen.findByText("No fee dues found")).toBeInTheDocument();
  });

  it("renders data state", async () => {
    vi.mocked(listFeeDues).mockResolvedValue({
      data: [
        {
          id: "due-1",
          organization: "org-1",
          branch: "branch-1",
          academic_year: "year-1",
          academic_period: null,
          student: "student-1",
          class_room: "class-1",
          class_enrollment: "enrollment-1",
          fee_plan: "plan-1",
          period_label: "Baisakh 2083",
          due_date_ad: "2026-04-15",
          due_date_bs: "",
          original_amount: "5000.00",
          discount_amount: "0.00",
          fine_amount: "0.00",
          net_amount: "5000.00",
          paid_amount: "1000.00",
          balance_amount: "4000.00",
          status: "partial",
          approved_by: null,
          approved_at: null,
          cancelled_by: null,
          cancelled_at: null,
          cancellation_reason: "",
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
      "/dashboard/billing/dues/due-1",
    );
    expect(screen.getByText("Partial")).toBeInTheDocument();
  });
});
