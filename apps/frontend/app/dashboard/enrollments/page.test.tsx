import React from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import EnrollmentsPage from "@/app/dashboard/enrollments/page";
import { listClassEnrollments } from "@/lib/classes";

vi.mock("@/lib/classes", () => ({
  listClassEnrollments: vi.fn(),
}));

function renderPage() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <EnrollmentsPage />
    </QueryClientProvider>,
  );
}

describe("EnrollmentsPage", () => {
  beforeEach(() => {
    vi.mocked(listClassEnrollments).mockReset();
  });

  it("renders loading state", () => {
    vi.mocked(listClassEnrollments).mockReturnValue(new Promise(() => undefined));
    renderPage();

    expect(screen.getByRole("status")).toHaveTextContent("Loading enrollments...");
  });

  it("renders empty state", async () => {
    vi.mocked(listClassEnrollments).mockResolvedValue({
      data: [],
      pagination: { count: 0, page: 1, page_size: 25, next: null, previous: null },
    });
    renderPage();

    expect(await screen.findByText("No enrollments found")).toBeInTheDocument();
  });

  it("renders data state", async () => {
    vi.mocked(listClassEnrollments).mockResolvedValue({
      data: [
        {
          id: "enrollment-1",
          organization: "org-1",
          branch: "branch-1",
          academic_year: "year-1",
          student: "student-1",
          class_room: "class-1",
          joined_date_ad: "2026-01-01",
          joined_date_bs: "",
          end_date_ad: null,
          end_date_bs: "",
          left_date_ad: null,
          left_date_bs: "",
          status: "active",
          enrollment_discount_percentage: null,
          enrollment_discount_amount: null,
          teacher_cut_percentage_override: null,
          notes: "",
          created_at: "2026-01-01T00:00:00Z",
          updated_at: "2026-01-01T00:00:00Z",
        },
      ],
      pagination: { count: 1, page: 1, page_size: 25, next: null, previous: null },
    });
    renderPage();

    expect(await screen.findByRole("link", { name: "enrollment-1" })).toHaveAttribute(
      "href",
      "/dashboard/enrollments/enrollment-1",
    );
    expect(screen.getByText("student-1")).toBeInTheDocument();
  });
});
