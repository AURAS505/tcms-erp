import React from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ReportFilters } from "@/components/reports/ReportFilters";
import { listAcademicYears, listBranches, listOrganizations } from "@/lib/lookups";

const push = vi.fn();

vi.mock("next/navigation", () => ({
  usePathname: () => "/dashboard/accounting/reports/trial-balance",
  useRouter: () => ({ push }),
  useSearchParams: () => ({ get: () => null }),
}));

vi.mock("@/lib/lookups", () => ({
  listOrganizations: vi.fn(),
  listBranches: vi.fn(),
  listAcademicYears: vi.fn(),
  listAcademicPeriods: vi.fn(),
}));

function renderFilters() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <ReportFilters />
    </QueryClientProvider>,
  );
}

describe("ReportFilters", () => {
  beforeEach(() => {
    push.mockReset();
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
  });

  it("renders organization selector and applies selected filters", async () => {
    renderFilters();

    const organizationSelect = await screen.findByLabelText(/organization/i);
    await screen.findByRole("option", { name: "TCMS" });
    fireEvent.change(organizationSelect, { target: { value: "org-1" } });
    await waitFor(() => expect(organizationSelect).toHaveValue("org-1"));
    fireEvent.change(screen.getByLabelText(/date from/i), { target: { value: "2026-01-01" } });
    fireEvent.click(screen.getByRole("button", { name: /apply filters/i }));

    await waitFor(() =>
      expect(push).toHaveBeenCalledWith(
        "/dashboard/accounting/reports/trial-balance?organization=org-1&date_from=2026-01-01",
      ),
    );
  });
});
