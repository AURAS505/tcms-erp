import { afterEach, describe, expect, it, vi } from "vitest";
import {
  approveJournalEntry,
  attachAccountingDocument,
  createManualJournalEntry,
  getAccount,
  getBalanceSheet,
  getGeneralLedger,
  getJournalEntry,
  getProfitLoss,
  getTrialBalance,
  listAccountingDocuments,
  listAccounts,
  listJournalEntries,
  listJournalEntryLines,
  postJournalEntry,
  reverseJournalEntry,
} from "@/lib/accounting";

const mockFetch = (data: unknown) => {
  const fetchMock = vi.fn().mockResolvedValue({
    ok: true,
    status: 200,
    json: vi.fn().mockResolvedValue({
      success: true,
      data,
      errors: null,
      meta: {
        pagination: {
          count: Array.isArray(data) ? data.length : 1,
          page: 1,
          page_size: 25,
          next: null,
          previous: null,
        },
      },
    }),
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
};

describe("accounting API client", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("calls expected accounting resource endpoints", async () => {
    const fetchMock = mockFetch([]);

    await listAccounts("cash");
    await getAccount("account-1");
    await listJournalEntries();
    await getJournalEntry("entry-1");
    await listJournalEntryLines("JE");
    await listAccountingDocuments();

    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      "http://localhost:8000/api/v1/accounts/?search=cash",
      expect.objectContaining({ credentials: "include" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      "http://localhost:8000/api/v1/accounts/account-1/",
      expect.objectContaining({ credentials: "include" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      3,
      "http://localhost:8000/api/v1/journal-entries/",
      expect.objectContaining({ credentials: "include" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      4,
      "http://localhost:8000/api/v1/journal-entries/entry-1/",
      expect.objectContaining({ credentials: "include" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      5,
      "http://localhost:8000/api/v1/journal-entry-lines/?search=JE",
      expect.objectContaining({ credentials: "include" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      6,
      "http://localhost:8000/api/v1/accounting-documents/",
      expect.objectContaining({ credentials: "include" }),
    );
  });

  it("calls expected accounting report endpoints", async () => {
    const fetchMock = mockFetch({ lines: [] });

    await getTrialBalance({ organization: "org-1", include_zero_balances: true });
    await getGeneralLedger({ organization: "org-1", account: "account-1" });
    await getProfitLoss({ organization: "org-1", date_from: "2026-01-01" });
    await getBalanceSheet({ organization: "org-1", date_to: "2026-12-31" });

    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      "http://localhost:8000/api/v1/reports/trial-balance/?organization=org-1&include_zero_balances=true",
      expect.objectContaining({ credentials: "include" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      "http://localhost:8000/api/v1/reports/general-ledger/?organization=org-1&account=account-1",
      expect.objectContaining({ credentials: "include" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      3,
      "http://localhost:8000/api/v1/reports/profit-loss/?organization=org-1&date_from=2026-01-01",
      expect.objectContaining({ credentials: "include" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      4,
      "http://localhost:8000/api/v1/reports/balance-sheet/?organization=org-1&date_to=2026-12-31",
      expect.objectContaining({ credentials: "include" }),
    );
  });

  it("calls expected accounting mutation endpoints", async () => {
    const fetchMock = mockFetch({ id: "entry-1" });

    await createManualJournalEntry({
      organization: "org-1",
      branch: "branch-1",
      academic_year: "year-1",
      academic_period: null,
      entry_date_ad: "2026-04-15",
      description: "Manual journal",
      narration: "Adjustment",
      lines: [
        { account: "cash", description: "Cash", debit_amount: "100.00", credit_amount: "0.00" },
        { account: "capital", description: "Capital", debit_amount: "0.00", credit_amount: "100.00" },
      ],
    });
    await approveJournalEntry("entry-1");
    await postJournalEntry("entry-1");
    await reverseJournalEntry("entry-1", { reversal_date_ad: "2026-04-16", narration: "Reverse entry" });
    await attachAccountingDocument("entry-1", { document_type: "voucher", reference_number: "VCH-001" });

    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      "http://localhost:8000/api/v1/journal-entries/create-manual/",
      expect.objectContaining({ method: "POST", body: expect.stringContaining('"lines"') }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      "http://localhost:8000/api/v1/journal-entries/entry-1/approve/",
      expect.objectContaining({ method: "POST", body: "{}" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      3,
      "http://localhost:8000/api/v1/journal-entries/entry-1/post/",
      expect.objectContaining({ method: "POST", body: "{}" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      4,
      "http://localhost:8000/api/v1/journal-entries/entry-1/reverse/",
      expect.objectContaining({ method: "POST", body: expect.stringContaining("Reverse entry") }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      5,
      "http://localhost:8000/api/v1/journal-entries/entry-1/documents/",
      expect.objectContaining({ method: "POST", body: expect.stringContaining("VCH-001") }),
    );
  });
});
