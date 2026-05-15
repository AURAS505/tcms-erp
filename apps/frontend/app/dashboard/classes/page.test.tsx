import React from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import ClassesPage from "@/app/dashboard/classes/page";
import { listClasses } from "@/lib/classes";

vi.mock("@/lib/classes", () => ({
  listClasses: vi.fn(),
}));

function renderPage() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <ClassesPage />
    </QueryClientProvider>,
  );
}

describe("ClassesPage", () => {
  beforeEach(() => {
    vi.mocked(listClasses).mockReset();
  });

  it("renders loading state", () => {
    vi.mocked(listClasses).mockReturnValue(new Promise(() => undefined));
    renderPage();

    expect(screen.getByRole("status")).toHaveTextContent("Loading classes...");
  });

  it("renders empty state", async () => {
    vi.mocked(listClasses).mockResolvedValue({
      data: [],
      pagination: { count: 0, page: 1, page_size: 25, next: null, previous: null },
    });
    renderPage();

    expect(await screen.findByText("No classes found")).toBeInTheDocument();
  });

  it("renders data state", async () => {
    vi.mocked(listClasses).mockResolvedValue({
      data: [
        {
          id: "class-1",
          class_name: "Grade 8 Math",
          batch_name: "Morning",
          section_name: "A",
          primary_teacher: null,
          subjects: ["subject-1"],
          start_date_ad: "2026-01-01",
          start_date_bs: "",
          expected_end_date_ad: null,
          expected_end_date_bs: "",
          capacity: 24,
          monthly_fee: "5000.00",
          teacher_cut_percentage: null,
          teacher_payment_type: "percentage",
          payment_due_rule: "monthly",
          due_day: 5,
          status: "active",
          notes: "",
          created_at: "2026-01-01T00:00:00Z",
          updated_at: "2026-01-01T00:00:00Z",
        },
      ],
      pagination: { count: 1, page: 1, page_size: 25, next: null, previous: null },
    });
    renderPage();

    expect(await screen.findByRole("link", { name: "Grade 8 Math" })).toHaveAttribute(
      "href",
      "/dashboard/classes/class-1",
    );
    expect(screen.getByText("Morning")).toBeInTheDocument();
  });
});
