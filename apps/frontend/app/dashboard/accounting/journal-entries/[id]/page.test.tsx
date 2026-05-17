import React from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import JournalEntryDetailPage from "@/app/dashboard/accounting/journal-entries/[id]/page";
import { useAuth } from "@/hooks/useAuth";
import {
  approveJournalEntry,
  attachAccountingDocument,
  getJournalEntry,
  listJournalEntryLines,
  postJournalEntry,
  reverseJournalEntry,
} from "@/lib/accounting";
import type { JournalEntry } from "@/types/accounting";

vi.mock("@/hooks/useAuth", () => ({
  useAuth: vi.fn(),
}));

vi.mock("@/lib/accounting", () => ({
  approveJournalEntry: vi.fn(),
  attachAccountingDocument: vi.fn(),
  getJournalEntry: vi.fn(),
  listJournalEntryLines: vi.fn(),
  postJournalEntry: vi.fn(),
  reverseJournalEntry: vi.fn(),
}));

const entry = (status: JournalEntry["status"]): JournalEntry => ({
  id: "entry-1",
  organization: "org-1",
  branch: "branch-1",
  academic_year: "year-1",
  academic_period: null,
  entry_number: "JV-000001",
  entry_date_ad: "2026-04-15",
  entry_date_bs: "",
  posting_date_ad: status === "posted" || status === "reversed" ? "2026-04-15" : null,
  posting_date_bs: "",
  description: "Manual adjustment",
  narration: "Correction",
  source_type: "manual",
  source_app: "",
  source_model: "",
  source_object_id: null,
  source_number: "",
  status,
  is_system_generated: false,
  created_by: null,
  approved_by: null,
  posted_by: null,
  reversed_entry: null,
  posted_at: status === "posted" || status === "reversed" ? "2026-04-15T00:00:00Z" : null,
  created_at: "",
  updated_at: "",
});

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
      <JournalEntryDetailPage params={{ id: "entry-1" }} />
    </QueryClientProvider>,
  );
}

describe("JournalEntryDetailPage", () => {
  beforeEach(() => {
    vi.mocked(approveJournalEntry).mockReset();
    vi.mocked(attachAccountingDocument).mockReset();
    vi.mocked(getJournalEntry).mockReset();
    vi.mocked(listJournalEntryLines).mockReset();
    vi.mocked(postJournalEntry).mockReset();
    vi.mocked(reverseJournalEntry).mockReset();
    mockRole("accountant");
    vi.mocked(listJournalEntryLines).mockResolvedValue({
      data: [
        {
          id: "line-1",
          journal_entry: "entry-1",
          organization: "org-1",
          branch: "branch-1",
          account: "1110",
          description: "Cash",
          debit_amount: "100.00",
          credit_amount: "0.00",
          student_id: null,
          teacher_id: null,
          class_id: null,
          created_at: "",
          updated_at: "",
        },
      ],
      pagination: { count: 1, page: 1, page_size: 25, next: null, previous: null },
    });
  });

  it("shows approve action for accounting role", async () => {
    vi.mocked(getJournalEntry).mockResolvedValue(entry("draft"));

    renderPage();

    expect(await screen.findByRole("button", { name: /approve journal/i })).toBeInTheDocument();
  });

  it("shows post action for approved journal", async () => {
    vi.mocked(getJournalEntry).mockResolvedValue(entry("approved"));

    renderPage();

    expect(await screen.findByRole("button", { name: /post journal/i })).toBeInTheDocument();
  });

  it("shows reverse action for posted journal", async () => {
    vi.mocked(getJournalEntry).mockResolvedValue(entry("posted"));

    renderPage();

    expect(await screen.findByRole("button", { name: /reverse journal/i })).toBeInTheDocument();
  });

  it("shows document reference action for accounting role", async () => {
    vi.mocked(getJournalEntry).mockResolvedValue(entry("posted"));

    renderPage();

    expect(await screen.findByRole("heading", { name: /add document reference/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /add document reference/i })).toBeInTheDocument();
  });

  it.each(["receptionist", "teacher", "auditor"])("hides mutation actions for %s", async (role) => {
    mockRole(role);
    vi.mocked(getJournalEntry).mockResolvedValue(entry("posted"));

    renderPage();

    expect(await screen.findByRole("heading", { name: "JV-000001", level: 1 })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /approve journal/i })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /post journal/i })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /reverse journal/i })).not.toBeInTheDocument();
    expect(screen.queryByRole("heading", { name: /add document reference/i })).not.toBeInTheDocument();
  });

  it("shows reversed journal as read-only", async () => {
    vi.mocked(getJournalEntry).mockResolvedValue(entry("reversed"));

    renderPage();

    expect(await screen.findByText(/This journal entry is reversed and is read-only/i)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /reverse journal/i })).not.toBeInTheDocument();
  });

  it("calls approve, post, and reverse helpers", async () => {
    vi.mocked(getJournalEntry).mockResolvedValue(entry("draft"));
    vi.mocked(approveJournalEntry).mockResolvedValue(entry("approved"));

    renderPage();
    fireEvent.click(await screen.findByRole("button", { name: /approve journal/i }));

    await waitFor(() => expect(approveJournalEntry).toHaveBeenCalledWith("entry-1"));

    vi.mocked(getJournalEntry).mockResolvedValue(entry("approved"));
    vi.mocked(postJournalEntry).mockResolvedValue(entry("posted"));
    renderPage();
    fireEvent.click(await screen.findByRole("button", { name: /post journal/i }));
    await waitFor(() => expect(postJournalEntry).toHaveBeenCalledWith("entry-1"));

    vi.mocked(getJournalEntry).mockResolvedValue(entry("posted"));
    vi.mocked(reverseJournalEntry).mockResolvedValue(entry("posted"));
    renderPage();
    fireEvent.click(await screen.findByRole("button", { name: /reverse journal/i }));
    await waitFor(() => expect(reverseJournalEntry).toHaveBeenCalledWith("entry-1", expect.objectContaining({ narration: expect.stringContaining("JV-000001") })));
  });

  it("submits document reference metadata through accounting helper", async () => {
    vi.mocked(getJournalEntry).mockResolvedValue(entry("posted"));
    vi.mocked(attachAccountingDocument).mockResolvedValue({
      id: "document-1",
      organization: "org-1",
      journal_entry: "entry-1",
      document_type: "voucher",
      reference_number: "VCH-001",
      file_path: "",
      description: "Voucher reference",
      uploaded_by: null,
      created_at: "",
      updated_at: "",
    });

    renderPage();
    await screen.findByRole("heading", { name: /add document reference/i });
    fireEvent.change(screen.getByLabelText(/document type/i), { target: { value: "voucher" } });
    fireEvent.change(screen.getByLabelText(/reference number/i), { target: { value: "VCH-001" } });
    fireEvent.change(screen.getByLabelText(/^description$/i), { target: { value: "Voucher reference" } });
    fireEvent.click(screen.getByRole("button", { name: /add document reference/i }));

    await waitFor(() =>
      expect(attachAccountingDocument).toHaveBeenCalledWith("entry-1", {
        document_type: "voucher",
        reference_number: "VCH-001",
        description: "Voucher reference",
      }),
    );
    expect(await screen.findByText("Document reference added.")).toBeInTheDocument();
  });
});
