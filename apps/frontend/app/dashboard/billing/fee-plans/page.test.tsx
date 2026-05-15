import React from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import FeePlansPage from "@/app/dashboard/billing/fee-plans/page";
import { listFeePlans } from "@/lib/billing";

vi.mock("@/lib/billing", () => ({
  listFeePlans: vi.fn(),
}));

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <FeePlansPage />
    </QueryClientProvider>,
  );
}

describe("FeePlansPage", () => {
  beforeEach(() => {
    vi.mocked(listFeePlans).mockReset();
  });

  it("renders loading state", () => {
    vi.mocked(listFeePlans).mockReturnValue(new Promise(() => undefined));
    renderPage();

    expect(screen.getByRole("status")).toHaveTextContent("Loading fee plans...");
  });

  it("renders empty state", async () => {
    vi.mocked(listFeePlans).mockResolvedValue({
      data: [],
      pagination: { count: 0, page: 1, page_size: 25, next: null, previous: null },
    });
    renderPage();

    expect(await screen.findByText("No fee plans found")).toBeInTheDocument();
  });

  it("renders data state", async () => {
    vi.mocked(listFeePlans).mockResolvedValue({
      data: [
        {
          id: "plan-1",
          organization: "org-1",
          branch: "branch-1",
          academic_year: "year-1",
          class_room: "class-1",
          name: "Monthly Tuition",
          fee_plan_type: "monthly",
          billing_frequency: "monthly",
          payment_due_rule: "fixed_bs_day",
          due_day: 5,
          is_active: true,
          notes: "",
          created_at: "2026-01-01T00:00:00Z",
          updated_at: "2026-01-01T00:00:00Z",
        },
      ],
      pagination: { count: 1, page: 1, page_size: 25, next: null, previous: null },
    });
    renderPage();

    expect(await screen.findByRole("link", { name: "Monthly Tuition" })).toHaveAttribute(
      "href",
      "/dashboard/billing/fee-plans/plan-1",
    );
    expect(screen.getAllByText("Monthly")).toHaveLength(2);
  });
});
