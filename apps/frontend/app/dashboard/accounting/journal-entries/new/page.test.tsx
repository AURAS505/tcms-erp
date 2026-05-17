import React from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import NewJournalEntryPage from "@/app/dashboard/accounting/journal-entries/new/page";
import { useAuth } from "@/hooks/useAuth";
import { createManualJournalEntry, listAccounts } from "@/lib/accounting";
import { listAcademicPeriods, listAcademicYears, listBranches, listOrganizations } from "@/lib/lookups";

const push = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push }),
}));

vi.mock("@/hooks/useAuth", () => ({
  useAuth: vi.fn(),
}));

vi.mock("@/lib/accounting", () => ({
  createManualJournalEntry: vi.fn(),
  listAccounts: vi.fn(),
}));

vi.mock("@/lib/lookups", () => ({
  listAcademicPeriods: vi.fn(),
  listAcademicYears: vi.fn(),
  listBranches: vi.fn(),
  listOrganizations: vi.fn(),
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
      <NewJournalEntryPage />
    </QueryClientProvider>,
  );
}

async function fillHeader() {
  await screen.findByRole("option", { name: "TCMS" });
  fireEvent.change(screen.getByLabelText(/organization/i), { target: { value: "org-1" } });
  fireEvent.change(screen.getByLabelText(/^branch$/i), { target: { value: "branch-1" } });
  fireEvent.change(screen.getByLabelText(/academic year/i), { target: { value: "year-1" } });
  fireEvent.change(screen.getByLabelText(/entry date$/i), { target: { value: "2026-04-15" } });
  fireEvent.change(screen.getByLabelText(/^description$/i), { target: { value: "Manual adjustment" } });
}

async function fillBalancedLines() {
  fireEvent.change(screen.getByLabelText(/account 1/i), { target: { value: "account-cash" } });
  fireEvent.change(screen.getByLabelText(/debit amount 1/i), { target: { value: "100.00" } });
  fireEvent.change(screen.getByLabelText(/account 2/i), { target: { value: "account-capital" } });
  fireEvent.change(screen.getByLabelText(/credit amount 2/i), { target: { value: "100.00" } });
}

describe("NewJournalEntryPage", () => {
  beforeEach(() => {
    push.mockReset();
    mockRole("accountant");
    vi.mocked(createManualJournalEntry).mockReset();
    vi.mocked(listOrganizations).mockResolvedValue({
      data: [{ id: "org-1", display_name: "TCMS", legal_name: "TCMS Pvt Ltd", is_active: true }],
      pagination: { count: 1, page: 1, page_size: 25, next: null, previous: null },
    });
    vi.mocked(listBranches).mockResolvedValue({
      data: [{ id: "branch-1", organization: "org-1", code: "MAIN", name: "Main Branch", is_active: true }],
      pagination: { count: 1, page: 1, page_size: 25, next: null, previous: null },
    });
    vi.mocked(listAcademicYears).mockResolvedValue({
      data: [{ id: "year-1", organization: "org-1", name: "2083", ad_start_date: "2026-04-14", ad_end_date: "2027-04-13", status: "active", is_active: true }],
      pagination: { count: 1, page: 1, page_size: 25, next: null, previous: null },
    });
    vi.mocked(listAcademicPeriods).mockResolvedValue({
      data: [{ id: "period-1", organization: "org-1", academic_year: "year-1", name: "Baishakh", ad_start_date: "2026-04-14", ad_end_date: "2026-05-14", status: "open", is_active: true }],
      pagination: { count: 1, page: 1, page_size: 25, next: null, previous: null },
    });
    vi.mocked(listAccounts).mockResolvedValue({
      data: [
        { id: "account-cash", organization: "org-1", code: "1110", name: "Cash", account_type: "asset", parent: null, normal_balance: "debit", is_system_account: false, is_active: true, description: "", created_at: "", updated_at: "" },
        { id: "account-capital", organization: "org-1", code: "3100", name: "Capital", account_type: "equity", parent: null, normal_balance: "credit", is_system_account: false, is_active: true, description: "", created_at: "", updated_at: "" },
      ],
      pagination: { count: 2, page: 1, page_size: 25, next: null, previous: null },
    });
  });

  it("renders line editor", async () => {
    renderPage();

    expect(await screen.findByRole("heading", { name: "New Journal Entry" })).toBeInTheDocument();
    expect(screen.getByLabelText(/account 1/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/debit amount 1/i)).toBeInTheDocument();
    expect(screen.getByText(/debit total:/i)).toBeInTheDocument();
  });

  it("blocks unbalanced submission", async () => {
    renderPage();
    await fillHeader();
    fireEvent.change(screen.getByLabelText(/account 1/i), { target: { value: "account-cash" } });
    fireEvent.change(screen.getByLabelText(/debit amount 1/i), { target: { value: "100.00" } });
    fireEvent.change(screen.getByLabelText(/account 2/i), { target: { value: "account-capital" } });
    fireEvent.change(screen.getByLabelText(/credit amount 2/i), { target: { value: "90.00" } });

    expect(screen.getByText(/debit and credit totals must balance/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /create draft journal/i })).toBeDisabled();
  });

  it("sends balanced draft payload and redirects", async () => {
    vi.mocked(createManualJournalEntry).mockResolvedValue({
      id: "entry-1",
      organization: "org-1",
      branch: "branch-1",
      academic_year: "year-1",
      academic_period: null,
      entry_number: "JV-000001",
      entry_date_ad: "2026-04-15",
      entry_date_bs: "",
      posting_date_ad: null,
      posting_date_bs: "",
      description: "Manual adjustment",
      narration: "",
      source_type: "manual",
      source_app: "",
      source_model: "",
      source_object_id: null,
      source_number: "",
      status: "draft",
      is_system_generated: false,
      created_by: null,
      approved_by: null,
      posted_by: null,
      reversed_entry: null,
      posted_at: null,
      created_at: "",
      updated_at: "",
    });
    renderPage();
    await fillHeader();
    await fillBalancedLines();
    fireEvent.click(screen.getByRole("button", { name: /create draft journal/i }));

    await waitFor(() => expect(createManualJournalEntry).toHaveBeenCalled());
    expect(vi.mocked(createManualJournalEntry).mock.calls[0][0]).toEqual(
      expect.objectContaining({
        organization: "org-1",
        branch: "branch-1",
        academic_year: "year-1",
        entry_date_ad: "2026-04-15",
        lines: [
          expect.objectContaining({ account: "account-cash", debit_amount: "100.00" }),
          expect.objectContaining({ account: "account-capital", credit_amount: "100.00" }),
        ],
      }),
    );
    await waitFor(() => expect(push).toHaveBeenCalledWith("/dashboard/accounting/journal-entries/entry-1"));
  });

  it("disables mutation for auditor", async () => {
    mockRole("auditor");
    renderPage();

    expect(await screen.findByText(/cannot create journal entries/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /create draft journal/i })).toBeDisabled();
  });
});
