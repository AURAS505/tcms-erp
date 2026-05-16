import React from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import TrialBalancePage from "@/app/dashboard/accounting/reports/trial-balance/page";
import { getTrialBalance } from "@/lib/accounting";

let organization: string | null = null;

vi.mock("next/navigation", () => ({
  useSearchParams: () => ({
    get: (key: string) => (key === "organization" ? organization : null),
  }),
}));

vi.mock("@/lib/accounting", () => ({
  getTrialBalance: vi.fn(),
}));

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <TrialBalancePage />
    </QueryClientProvider>,
  );
}

describe("TrialBalancePage", () => {
  beforeEach(() => {
    organization = null;
    vi.mocked(getTrialBalance).mockReset();
  });

  it("renders filter-required state without organization", () => {
    renderPage();

    expect(screen.getByText("Report filters required")).toBeInTheDocument();
    expect(getTrialBalance).not.toHaveBeenCalled();
  });

  it("renders report data", async () => {
    organization = "org-1";
    vi.mocked(getTrialBalance).mockResolvedValue({
      lines: [
        {
          account_code: "1110",
          account_name: "Cash",
          account_type: "asset",
          normal_balance: "debit",
          debit: "5000.00",
          credit: "0.00",
          balance: "5000.00",
          is_abnormal: false,
        },
      ],
      total_debit: "5000.00",
      total_credit: "5000.00",
      is_balanced: true,
      difference: "0.00",
    });
    renderPage();

    expect(await screen.findByText("1110 - Cash")).toBeInTheDocument();
    expect(screen.getByText("Balanced")).toBeInTheDocument();
  });
});
