import React from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import FamiliesPage from "@/app/dashboard/families/page";
import { listFamilies } from "@/lib/guardians";

vi.mock("@/lib/guardians", () => ({
  listFamilies: vi.fn(),
}));

function renderPage() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <FamiliesPage />
    </QueryClientProvider>,
  );
}

describe("FamiliesPage", () => {
  beforeEach(() => {
    vi.mocked(listFamilies).mockReset();
  });

  it("renders loading state", () => {
    vi.mocked(listFamilies).mockReturnValue(new Promise(() => undefined));
    renderPage();

    expect(screen.getByRole("status")).toHaveTextContent("Loading families...");
  });

  it("renders empty state", async () => {
    vi.mocked(listFamilies).mockResolvedValue({
      data: [],
      pagination: { count: 0, page: 1, page_size: 25, next: null, previous: null },
    });
    renderPage();

    expect(await screen.findByText("No families found")).toBeInTheDocument();
  });

  it("renders data state", async () => {
    vi.mocked(listFamilies).mockResolvedValue({
      data: [
        {
          id: "family-1",
          family_code: "FAM-001",
          primary_contact_name: "Rita Sharma",
          primary_contact_number: "9800000000",
          address: "Kathmandu",
          notes: "",
          is_active: true,
          created_at: "2026-01-01T00:00:00Z",
          updated_at: "2026-01-01T00:00:00Z",
        },
      ],
      pagination: { count: 1, page: 1, page_size: 25, next: null, previous: null },
    });
    renderPage();

    expect(await screen.findByRole("link", { name: "FAM-001" })).toHaveAttribute(
      "href",
      "/dashboard/families/family-1",
    );
    expect(screen.getByText("Rita Sharma")).toBeInTheDocument();
  });
});

