import React from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import TeacherContractsPage from "@/app/dashboard/teacher-contracts/page";
import { listTeacherContracts } from "@/lib/teachers";

vi.mock("@/lib/teachers", () => ({
  listTeacherContracts: vi.fn(),
}));

function renderPage() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <TeacherContractsPage />
    </QueryClientProvider>,
  );
}

describe("TeacherContractsPage", () => {
  beforeEach(() => {
    vi.mocked(listTeacherContracts).mockReset();
  });

  it("renders loading state", () => {
    vi.mocked(listTeacherContracts).mockReturnValue(new Promise(() => undefined));
    renderPage();

    expect(screen.getByRole("status")).toHaveTextContent("Loading teacher contracts...");
  });

  it("renders empty state", async () => {
    vi.mocked(listTeacherContracts).mockResolvedValue({
      data: [],
      pagination: { count: 0, page: 1, page_size: 25, next: null, previous: null },
    });
    renderPage();

    expect(await screen.findByText("No teacher contracts found")).toBeInTheDocument();
  });

  it("renders data state", async () => {
    vi.mocked(listTeacherContracts).mockResolvedValue({
      data: [
        {
          id: "contract-1",
          teacher: "teacher-1",
          organization: "org-1",
          branch: "branch-1",
          academic_year: "year-1",
          contract_type: "monthly_cut_percentage",
          default_teacher_cut_percentage: "50.0000",
          package_amount: null,
          fixed_monthly_salary: null,
          effective_from_ad: "2026-01-01",
          effective_from_bs: "",
          effective_to_ad: null,
          effective_to_bs: "",
          is_active: true,
          notes: "",
          created_at: "2026-01-01T00:00:00Z",
          updated_at: "2026-01-01T00:00:00Z",
        },
      ],
      pagination: { count: 1, page: 1, page_size: 25, next: null, previous: null },
    });
    renderPage();

    expect(await screen.findByRole("link", { name: "contract-1" })).toHaveAttribute(
      "href",
      "/dashboard/teacher-contracts/contract-1",
    );
    expect(screen.getByText("Monthly Cut Percentage")).toBeInTheDocument();
  });
});
