import React from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import StudentInquiriesPage from "@/app/dashboard/student-inquiries/page";
import { listStudentInquiries } from "@/lib/students";

vi.mock("@/lib/students", () => ({
  listStudentInquiries: vi.fn(),
}));

function renderPage() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <StudentInquiriesPage />
    </QueryClientProvider>,
  );
}

describe("StudentInquiriesPage", () => {
  beforeEach(() => {
    vi.mocked(listStudentInquiries).mockReset();
  });

  it("renders loading state", () => {
    vi.mocked(listStudentInquiries).mockReturnValue(new Promise(() => undefined));
    renderPage();

    expect(screen.getByRole("status")).toHaveTextContent("Loading inquiries...");
  });

  it("renders empty state", async () => {
    vi.mocked(listStudentInquiries).mockResolvedValue({
      data: [],
      pagination: { count: 0, page: 1, page_size: 25, next: null, previous: null },
    });
    renderPage();

    expect(await screen.findByText("No inquiries found")).toBeInTheDocument();
  });

  it("renders data state", async () => {
    vi.mocked(listStudentInquiries).mockResolvedValue({
      data: [
        {
          id: "inquiry-1",
          student_full_name: "Asha Sharma",
          guardian_name: "Rita Sharma",
          contact_number: "9800000000",
          email: "",
          interested_class_subject: "Grade 8",
          inquiry_source: "walk-in",
          status: "new",
          notes: "",
          created_at: "2026-01-01T00:00:00Z",
          updated_at: "2026-01-01T00:00:00Z",
        },
      ],
      pagination: { count: 1, page: 1, page_size: 25, next: null, previous: null },
    });
    renderPage();

    expect(await screen.findByRole("link", { name: "Asha Sharma" })).toHaveAttribute(
      "href",
      "/dashboard/student-inquiries/inquiry-1",
    );
    expect(screen.getByText("Rita Sharma")).toBeInTheDocument();
  });
});

