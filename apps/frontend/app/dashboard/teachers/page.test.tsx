import React from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import TeachersPage from "@/app/dashboard/teachers/page";
import { listTeachers } from "@/lib/teachers";

vi.mock("@/lib/teachers", () => ({
  listTeachers: vi.fn(),
}));

function renderPage() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <TeachersPage />
    </QueryClientProvider>,
  );
}

describe("TeachersPage", () => {
  beforeEach(() => {
    vi.mocked(listTeachers).mockReset();
  });

  it("renders loading state", () => {
    vi.mocked(listTeachers).mockReturnValue(new Promise(() => undefined));
    renderPage();

    expect(screen.getByRole("status")).toHaveTextContent("Loading teachers...");
  });

  it("renders empty state", async () => {
    vi.mocked(listTeachers).mockResolvedValue({
      data: [],
      pagination: { count: 0, page: 1, page_size: 25, next: null, previous: null },
    });
    renderPage();

    expect(await screen.findByText("No teachers found")).toBeInTheDocument();
  });

  it("renders data state", async () => {
    vi.mocked(listTeachers).mockResolvedValue({
      data: [
        {
          id: "teacher-1",
          organization: "org-1",
          branch: "branch-1",
          user: null,
          employee_number: "T-001",
          full_name: "Rita Sharma",
          preferred_name: "Rita",
          gender: "female",
          date_of_birth_ad: null,
          date_of_birth_bs: "",
          phone: "9800000000",
          alternate_phone: "",
          email: "rita@example.com",
          address: "Kathmandu",
          qualification: "MSc",
          specialization: "Mathematics",
          experience_summary: "",
          joining_date_ad: "2026-01-01",
          joining_date_bs: "",
          photo_path: "",
          status: "active",
          notes: "",
          created_at: "2026-01-01T00:00:00Z",
          updated_at: "2026-01-01T00:00:00Z",
        },
      ],
      pagination: { count: 1, page: 1, page_size: 25, next: null, previous: null },
    });
    renderPage();

    expect(await screen.findByRole("link", { name: "T-001" })).toHaveAttribute("href", "/dashboard/teachers/teacher-1");
    expect(screen.getByText("Rita Sharma")).toBeInTheDocument();
  });
});
