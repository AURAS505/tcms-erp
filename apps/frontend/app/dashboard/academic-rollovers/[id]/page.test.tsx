import React from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import AcademicRolloverDetailPage from "@/app/dashboard/academic-rollovers/[id]/page";
import { useAuth } from "@/hooks/useAuth";
import { cancelAcademicRollover, executeAcademicRollover, getAcademicRollover, getAcademicRolloverSummary, validateAcademicRollover } from "@/lib/academic";
import { listJournalEntries } from "@/lib/accounting";

vi.mock("@/hooks/useAuth", () => ({ useAuth: vi.fn() }));
vi.mock("@/lib/academic", () => ({
  cancelAcademicRollover: vi.fn(),
  executeAcademicRollover: vi.fn(),
  getAcademicRollover: vi.fn(),
  getAcademicRolloverSummary: vi.fn(),
  validateAcademicRollover: vi.fn(),
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

const rollover = {
  id: "rollover-1",
  organization: "org-1",
  from_academic_year: "year-1",
  to_academic_year: null,
  status: "ready" as const,
  trial_balance_validated: true,
  revenue_expense_closing_completed: false,
  opening_balances_posted: false,
  executed_by: null,
  executed_at: null,
  notes: "",
  created_at: "",
  updated_at: "",
};

const generatedJournal = {
  id: "journal-1",
  organization: "org-1",
  branch: null,
  academic_year: "year-1",
  academic_period: null,
  entry_number: "JV-ROLL-001",
  entry_date_ad: "2026-04-13",
  entry_date_bs: "2082-12-30",
  posting_date_ad: "2026-04-13",
  posting_date_bs: "2082-12-30",
  description: "Close revenue accounts",
  narration: "",
  source_type: "system",
  source_app: "academic",
  source_model: "AcademicYearRollover",
  source_object_id: "rollover-1",
  source_number: "closing-revenue",
  status: "posted" as const,
  debit_total: "1000.00",
  credit_total: "1000.00",
  is_system_generated: true,
  created_by: null,
  approved_by: null,
  posted_by: null,
  reversed_entry: null,
  posted_at: "2026-04-13T00:00:00Z",
  created_at: "",
  updated_at: "",
};

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <AcademicRolloverDetailPage params={{ id: "rollover-1" }} />
    </QueryClientProvider>,
  );
}

describe("AcademicRolloverDetailPage", () => {
  beforeEach(() => {
    mockRole("super_admin");
    vi.mocked(cancelAcademicRollover).mockReset();
    vi.mocked(executeAcademicRollover).mockReset();
    vi.mocked(getAcademicRollover).mockResolvedValue(rollover);
    vi.mocked(getAcademicRolloverSummary).mockResolvedValue({
      id: "rollover-1",
      organization: "TCMS",
      from_academic_year: "2083/2084",
      to_academic_year: null,
      status: "ready",
      trial_balance_validated: true,
      revenue_expense_closing_completed: false,
      opening_balances_posted: false,
      executed_at: null,
    });
    vi.mocked(listJournalEntries).mockResolvedValue({
      data: [generatedJournal],
      pagination: { count: 1, page: 1, page_size: 25, next: null, previous: null },
    });
    vi.mocked(validateAcademicRollover).mockReset();
  });

  it("shows rollover actions for super admin", async () => {
    renderPage();

    expect(await screen.findByRole("button", { name: /execute rollover/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /cancel/i })).toBeInTheDocument();
  });

  it("hides mutation actions for auditor", async () => {
    mockRole("auditor");
    renderPage();

    expect(await screen.findByText(/Source year:/i)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /execute rollover/i })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /cancel/i })).not.toBeInTheDocument();
  });

  it("execute action calls backend helper", async () => {
    vi.mocked(executeAcademicRollover).mockResolvedValue({ ...rollover, status: "executed" });
    renderPage();

    await screen.findByRole("button", { name: /execute rollover/i });
    fireEvent.change(screen.getByLabelText(/new year name/i), { target: { value: "2084/2085" } });
    fireEvent.change(screen.getByLabelText(/bs start year/i), { target: { value: "2084" } });
    fireEvent.change(screen.getByLabelText(/bs end year/i), { target: { value: "2085" } });
    fireEvent.change(screen.getByLabelText(/bs start date/i), { target: { value: "2084-01-01" } });
    fireEvent.change(screen.getByLabelText(/bs end date/i), { target: { value: "2084-12-30" } });
    fireEvent.change(screen.getByLabelText(/ad start date/i), { target: { value: "2027-04-14" } });
    fireEvent.change(screen.getByLabelText(/ad end date/i), { target: { value: "2028-04-13" } });
    fireEvent.click(screen.getByRole("button", { name: /execute rollover/i }));

    await waitFor(() => expect(executeAcademicRollover).toHaveBeenCalledWith("rollover-1", expect.objectContaining({ hard_close: true })));
  });

  it("renders generated journal entries as read-only links", async () => {
    renderPage();

    expect(await screen.findByText(/generated journal entries/i)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "JV-ROLL-001" })).toHaveAttribute("href", "/dashboard/accounting/journal-entries/journal-1");
    expect(screen.getByText(/close revenue accounts/i)).toBeInTheDocument();
    expect(listJournalEntries).toHaveBeenCalledWith({
      source_app: "academic",
      source_model: "AcademicYearRollover",
      source_object_id: "rollover-1",
      source_type: "system",
    });
  });

  it("shows an empty state when no generated journals exist", async () => {
    vi.mocked(listJournalEntries).mockResolvedValue({
      data: [],
      pagination: { count: 0, page: 1, page_size: 25, next: null, previous: null },
    });

    renderPage();

    expect(await screen.findByText(/no generated journal entries found/i)).toBeInTheDocument();
  });
});
