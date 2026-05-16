import React from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import TrialBalancePage from "@/app/dashboard/accounting/reports/trial-balance/page";
import { getTrialBalance } from "@/lib/accounting";
import { listAcademicPeriods, listAcademicYears, listBranches, listOrganizations } from "@/lib/lookups";

let organization: string | null = null;

vi.mock("next/navigation", () => ({
  usePathname: () => "/dashboard/accounting/reports/trial-balance",
  useRouter: () => ({ push: vi.fn() }),
  useSearchParams: () => ({
    get: (key: string) => (key === "organization" ? organization : null),
  }),
}));

vi.mock("@/lib/accounting", () => ({
  getTrialBalance: vi.fn(),
}));

vi.mock("@/lib/lookups", () => ({
  listOrganizations: vi.fn(),
  listBranches: vi.fn(),
  listAcademicYears: vi.fn(),
  listAcademicPeriods: vi.fn(),
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
    vi.mocked(listOrganizations).mockResolvedValue({
      data: [{ id: "org-1", display_name: "TCMS", legal_name: "TCMS Pvt Ltd", is_active: true }],
      pagination: { count: 1, page: 1, page_size: 25, next: null, previous: null },
    });
    vi.mocked(listBranches).mockResolvedValue({
      data: [],
      pagination: { count: 0, page: 1, page_size: 25, next: null, previous: null },
    });
    vi.mocked(listAcademicYears).mockResolvedValue({
      data: [],
      pagination: { count: 0, page: 1, page_size: 25, next: null, previous: null },
    });
    vi.mocked(listAcademicPeriods).mockResolvedValue({
      data: [],
      pagination: { count: 0, page: 1, page_size: 25, next: null, previous: null },
    });
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
    expect(getTrialBalance).toHaveBeenCalledWith(expect.objectContaining({ organization: "org-1" }));
    expect(screen.getByText("Balanced")).toBeInTheDocument();
  });
});
