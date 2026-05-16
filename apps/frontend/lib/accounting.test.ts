import { afterEach, describe, expect, it, vi } from "vitest";
import {
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
});
