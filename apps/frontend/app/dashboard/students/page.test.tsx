import React from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import StudentsPage from "@/app/dashboard/students/page";
import { listStudents } from "@/lib/students";

vi.mock("@/lib/students", () => ({
  listStudents: vi.fn(),
}));

function renderPage() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <StudentsPage />
    </QueryClientProvider>,
  );
}

describe("StudentsPage", () => {
  beforeEach(() => {
    vi.mocked(listStudents).mockReset();
  });

  it("renders loading state", () => {
    vi.mocked(listStudents).mockReturnValue(new Promise(() => undefined));
    renderPage();

    expect(screen.getByRole("status")).toHaveTextContent("Loading students...");
  });

  it("renders empty state", async () => {
    vi.mocked(listStudents).mockResolvedValue({
      data: [],
      pagination: { count: 0, page: 1, page_size: 25, next: null, previous: null },
    });
    renderPage();

    expect(await screen.findByText("No students found")).toBeInTheDocument();
  });

  it("renders data state", async () => {
    vi.mocked(listStudents).mockResolvedValue({
      data: [
        {
          id: "student-1",
          admission_number: "ADM-001",
          full_name: "Asha Sharma",
          preferred_name: "",
          gender: "female",
          date_of_birth_ad: null,
          date_of_birth_bs: "",
          phone: "9800000000",
          email: "",
          permanent_address: "Kathmandu",
          temporary_address: "",
          school_college_name: "",
          current_grade_class: "Grade 8",
          status: "active",
          admission_date_ad: null,
          admission_date_bs: "",
          notes: "",
          created_at: "2026-01-01T00:00:00Z",
          updated_at: "2026-01-01T00:00:00Z",
        },
      ],
      pagination: { count: 1, page: 1, page_size: 25, next: null, previous: null },
    });
    renderPage();

    expect(await screen.findByRole("link", { name: "ADM-001" })).toHaveAttribute(
      "href",
      "/dashboard/students/student-1",
    );
    expect(screen.getByText("Asha Sharma")).toBeInTheDocument();
  });
});

