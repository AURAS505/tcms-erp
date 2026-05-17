import React from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import JournalEntriesPage from "@/app/dashboard/accounting/journal-entries/page";
import { useAuth } from "@/hooks/useAuth";
import { listJournalEntries } from "@/lib/accounting";

vi.mock("@/hooks/useAuth", () => ({
  useAuth: vi.fn(),
}));

vi.mock("@/lib/accounting", () => ({
  listJournalEntries: vi.fn(),
}));

function mockRole(role: string) {
  vi.mocked(useAuth).mockReturnValue({
    branchAssignments: [],
    error: null,
    hasPermission: vi.fn(() => false),
    hasRole: vi.fn((candidate) => candidate === role),
    isAuthenticated: true,
    isLoading: false,
    login: vi.fn(),
    logout: vi.fn(),
    permissions: [],
    refreshSession: vi.fn(),
    user: null,
  });
}

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <JournalEntriesPage />
    </QueryClientProvider>,
  );
}

describe("JournalEntriesPage", () => {
  beforeEach(() => {
    vi.mocked(listJournalEntries).mockReset();
    mockRole("accountant");
  });

  it("renders loading state", () => {
    vi.mocked(listJournalEntries).mockReturnValue(new Promise(() => undefined));
    renderPage();

    expect(screen.getByRole("status")).toHaveTextContent("Loading journal entries...");
  });

  it("renders empty state", async () => {
    vi.mocked(listJournalEntries).mockResolvedValue({
      data: [],
      pagination: { count: 0, page: 1, page_size: 25, next: null, previous: null },
    });
    renderPage();

    expect(await screen.findByText("No journal entries found")).toBeInTheDocument();
  });

  it("renders data state", async () => {
    vi.mocked(listJournalEntries).mockResolvedValue({
      data: [
        {
          id: "entry-1",
          organization: "org-1",
          branch: null,
          academic_year: "year-1",
          academic_period: null,
          entry_number: "JE-001",
          entry_date_ad: "2026-04-15",
          entry_date_bs: "",
          posting_date_ad: "2026-04-15",
          posting_date_bs: "",
          description: "Receipt posting",
          narration: "",
          source_type: "system",
          source_app: "billing",
          source_model: "StudentPayment",
          source_object_id: null,
          source_number: "RCPT-001",
          status: "posted",
          is_system_generated: true,
          created_by: null,
          approved_by: null,
          posted_by: null,
          reversed_entry: null,
          posted_at: "2026-04-15T00:00:00Z",
          created_at: "2026-01-01T00:00:00Z",
          updated_at: "2026-01-01T00:00:00Z",
        },
      ],
      pagination: { count: 1, page: 1, page_size: 25, next: null, previous: null },
    });
    renderPage();

    expect(await screen.findByRole("link", { name: "JE-001" })).toHaveAttribute(
      "href",
      "/dashboard/accounting/journal-entries/entry-1",
    );
    expect(screen.getByText("Receipt posting")).toBeInTheDocument();
  });

  it("shows new journal action for accounting role", async () => {
    vi.mocked(listJournalEntries).mockResolvedValue({
      data: [],
      pagination: { count: 0, page: 1, page_size: 25, next: null, previous: null },
    });
    renderPage();

    expect(await screen.findByRole("link", { name: /new journal entry/i })).toHaveAttribute(
      "href",
      "/dashboard/accounting/journal-entries/new",
    );
  });

  it("hides new journal action for auditor", async () => {
    mockRole("auditor");
    vi.mocked(listJournalEntries).mockResolvedValue({
      data: [],
      pagination: { count: 0, page: 1, page_size: 25, next: null, previous: null },
    });
    renderPage();

    await screen.findByText("No journal entries found");
    expect(screen.queryByRole("link", { name: /new journal entry/i })).not.toBeInTheDocument();
  });
});
