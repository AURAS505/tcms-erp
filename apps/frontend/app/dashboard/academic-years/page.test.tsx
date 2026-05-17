import React from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import AcademicYearsPage from "@/app/dashboard/academic-years/page";
import { listAcademicYears } from "@/lib/academic";

vi.mock("@/lib/academic", () => ({
  listAcademicYears: vi.fn(),
}));

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <AcademicYearsPage />
    </QueryClientProvider>,
  );
}

describe("AcademicYearsPage", () => {
  beforeEach(() => vi.mocked(listAcademicYears).mockReset());

  it("renders academic years list", async () => {
    vi.mocked(listAcademicYears).mockResolvedValue({
      data: [
        {
          id: "year-1",
          organization: "org-1",
          name: "2083/2084",
          bs_start_year: 2083,
          bs_end_year: 2084,
          bs_start_date: "2083-01-01",
          bs_end_date: "2083-12-30",
          ad_start_date: "2026-04-14",
          ad_end_date: "2027-04-13",
          status: "active",
          is_active: true,
          notes: "",
          created_at: "",
          updated_at: "",
        },
      ],
      pagination: { count: 1, page: 1, page_size: 25, next: null, previous: null },
    });

    renderPage();

    expect(await screen.findByRole("link", { name: "2083/2084" })).toHaveAttribute("href", "/dashboard/academic-years/year-1");
    expect(screen.getByText("2026-04-14 to 2027-04-13")).toBeInTheDocument();
  });
});
