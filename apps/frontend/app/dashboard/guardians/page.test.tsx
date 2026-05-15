import React from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import GuardiansPage from "@/app/dashboard/guardians/page";
import { listGuardians } from "@/lib/guardians";

vi.mock("@/lib/guardians", () => ({
  listGuardians: vi.fn(),
}));

function renderPage() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <GuardiansPage />
    </QueryClientProvider>,
  );
}

describe("GuardiansPage", () => {
  beforeEach(() => {
    vi.mocked(listGuardians).mockReset();
  });

  it("renders loading state", () => {
    vi.mocked(listGuardians).mockReturnValue(new Promise(() => undefined));
    renderPage();

    expect(screen.getByRole("status")).toHaveTextContent("Loading guardians...");
  });

  it("renders empty state", async () => {
    vi.mocked(listGuardians).mockResolvedValue({
      data: [],
      pagination: { count: 0, page: 1, page_size: 25, next: null, previous: null },
    });
    renderPage();

    expect(await screen.findByText("No guardians found")).toBeInTheDocument();
  });

  it("renders data state", async () => {
    vi.mocked(listGuardians).mockResolvedValue({
      data: [
        {
          id: "guardian-1",
          family: "family-1",
          full_name: "Rita Sharma",
          relationship_type: "mother",
          phone: "9800000000",
          alternate_phone: "",
          email: "",
          occupation: "Teacher",
          address: "Kathmandu",
          is_primary_contact: true,
          is_active: true,
          created_at: "2026-01-01T00:00:00Z",
          updated_at: "2026-01-01T00:00:00Z",
        },
      ],
      pagination: { count: 1, page: 1, page_size: 25, next: null, previous: null },
    });
    renderPage();

    expect(await screen.findByRole("link", { name: "Rita Sharma" })).toHaveAttribute(
      "href",
      "/dashboard/guardians/guardian-1",
    );
    expect(screen.getByText("Teacher")).toBeInTheDocument();
  });
});

