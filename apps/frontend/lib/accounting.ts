import { apiClient, apiClientEnvelope } from "@/lib/api-client";
import type {
  Account,
  AccountingDocument,
  AccountingReportFilters,
  BalanceSheetReport,
  GeneralLedgerReport,
  JournalEntry,
  JournalEntryLine,
  ProfitLossReport,
  TrialBalanceReport,
} from "@/types/accounting";
import type { PaginatedResponse } from "@/types/students";

const ACCOUNTING_API_BASE = "/api/v1";

function buildListPath(path: string, search?: string) {
  const params = new URLSearchParams();
  if (search) params.set("search", search);
  const query = params.toString();
  return query ? `${path}?${query}` : path;
}

function buildReportPath(path: string, filters: AccountingReportFilters = {}) {
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([key, value]) => {
    if (value === undefined || value === null || value === "") return;
    params.set(key, typeof value === "boolean" ? String(value) : value);
  });
  const query = params.toString();
  return query ? `${path}?${query}` : path;
}

async function listResource<T>(path: string): Promise<PaginatedResponse<T>> {
  const envelope = await apiClientEnvelope<T[]>(path);
  return {
    data: envelope.data,
    pagination: envelope.meta?.pagination as PaginatedResponse<T>["pagination"],
  };
}

export function listAccounts(search?: string) {
  return listResource<Account>(buildListPath(`${ACCOUNTING_API_BASE}/accounts/`, search));
}

export function getAccount(id: string) {
  return apiClient<Account>(`${ACCOUNTING_API_BASE}/accounts/${id}/`);
}

export function listJournalEntries(search?: string) {
  return listResource<JournalEntry>(buildListPath(`${ACCOUNTING_API_BASE}/journal-entries/`, search));
}

export function getJournalEntry(id: string) {
  return apiClient<JournalEntry>(`${ACCOUNTING_API_BASE}/journal-entries/${id}/`);
}

export function listJournalEntryLines(search?: string) {
  return listResource<JournalEntryLine>(buildListPath(`${ACCOUNTING_API_BASE}/journal-entry-lines/`, search));
}

export function listAccountingDocuments(search?: string) {
  return listResource<AccountingDocument>(buildListPath(`${ACCOUNTING_API_BASE}/accounting-documents/`, search));
}

export function getTrialBalance(filters?: AccountingReportFilters) {
  return apiClient<TrialBalanceReport>(buildReportPath(`${ACCOUNTING_API_BASE}/reports/trial-balance/`, filters));
}

export function getGeneralLedger(filters?: AccountingReportFilters) {
  return apiClient<GeneralLedgerReport>(buildReportPath(`${ACCOUNTING_API_BASE}/reports/general-ledger/`, filters));
}

export function getProfitLoss(filters?: AccountingReportFilters) {
  return apiClient<ProfitLossReport>(buildReportPath(`${ACCOUNTING_API_BASE}/reports/profit-loss/`, filters));
}

export function getBalanceSheet(filters?: AccountingReportFilters) {
  return apiClient<BalanceSheetReport>(buildReportPath(`${ACCOUNTING_API_BASE}/reports/balance-sheet/`, filters));
}
