import React from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import SubjectsPage from "@/app/dashboard/subjects/page";
import { listSubjects } from "@/lib/classes";

vi.mock("@/lib/classes", () => ({
  listSubjects: vi.fn(),
}));

function renderPage() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <SubjectsPage />
    </QueryClientProvider>,
  );
}

describe("SubjectsPage", () => {
  beforeEach(() => {
    vi.mocked(listSubjects).mockReset();
  });

  it("renders loading state", () => {
    vi.mocked(listSubjects).mockReturnValue(new Promise(() => undefined));
    renderPage();

    expect(screen.getByRole("status")).toHaveTextContent("Loading subjects...");
  });

  it("renders empty state", async () => {
    vi.mocked(listSubjects).mockResolvedValue({
      data: [],
      pagination: { count: 0, page: 1, page_size: 25, next: null, previous: null },
    });
    renderPage();

    expect(await screen.findByText("No subjects found")).toBeInTheDocument();
  });

  it("renders data state", async () => {
    vi.mocked(listSubjects).mockResolvedValue({
      data: [
        {
          id: "subject-1",
          subject_code: "MATH-8",
          subject_name: "Mathematics",
          description: "Core mathematics",
          is_active: true,
          created_at: "2026-01-01T00:00:00Z",
          updated_at: "2026-01-01T00:00:00Z",
        },
      ],
      pagination: { count: 1, page: 1, page_size: 25, next: null, previous: null },
    });
    renderPage();

    expect(await screen.findByRole("link", { name: "MATH-8" })).toHaveAttribute(
      "href",
      "/dashboard/subjects/subject-1",
    );
    expect(screen.getByText("Mathematics")).toBeInTheDocument();
  });
});
