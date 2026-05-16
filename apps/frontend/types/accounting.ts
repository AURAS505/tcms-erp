import type { PaginatedResponse } from "@/types/students";

export type AccountType =
  | "asset"
  | "liability"
  | "equity"
  | "revenue"
  | "expense"
  | "contra_asset"
  | "contra_revenue"
  | "other_income"
  | "other_expense";
export type NormalBalance = "debit" | "credit";
export type JournalEntryStatus = "draft" | "pending_approval" | "approved" | "posted" | "reversed" | "void";

export interface Account {
  id: string;
  organization: string;
  code: string;
  name: string;
  account_type: AccountType;
  parent: string | null;
  normal_balance: NormalBalance;
  is_system_account: boolean;
  is_active: boolean;
  description: string;
  created_at: string;
  updated_at: string;
}

export interface JournalEntry {
  id: string;
  organization: string;
  branch: string | null;
  academic_year: string;
  academic_period: string | null;
  entry_number: string;
  entry_date_ad: string;
  entry_date_bs: string;
  posting_date_ad: string | null;
  posting_date_bs: string;
  description: string;
  narration: string;
  source_type: string;
  source_app: string;
  source_model: string;
  source_object_id: string | null;
  source_number: string;
  status: JournalEntryStatus;
  is_system_generated: boolean;
  created_by: string | null;
  approved_by: string | null;
  posted_by: string | null;
  reversed_entry: string | null;
  posted_at: string | null;
  created_at: string;
  updated_at: string;
  lines?: JournalEntryLine[];
}

export interface JournalEntryLine {
  id: string;
  journal_entry: string;
  organization: string;
  branch: string | null;
  account: string;
  description: string;
  debit_amount: string;
  credit_amount: string;
  student_id: string | null;
  teacher_id: string | null;
  class_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface AccountingDocument {
  id: string;
  organization: string;
  journal_entry: string | null;
  document_type: string;
  reference_number: string;
  file_path: string;
  description: string;
  uploaded_by: string | null;
  created_at: string;
  updated_at: string;
}

export interface AccountBalance {
  account_code: string;
  account_name: string;
  account_type: AccountType;
  normal_balance: NormalBalance;
  debit: string;
  credit: string;
  balance: string;
  is_abnormal?: boolean;
}

export interface TrialBalanceReport {
  lines: AccountBalance[];
  total_debit: string;
  total_credit: string;
  is_balanced: boolean;
  difference: string;
}

export interface LedgerTransaction {
  entry_date: string;
  entry_number: string;
  description: string;
  narration: string;
  debit: string;
  credit: string;
  running_balance: string;
  source_app: string;
  source_model: string;
  source_object_id: string;
  source_number: string;
}

export interface AccountLedger {
  account_code: string;
  account_name: string;
  opening_balance: string;
  transactions: LedgerTransaction[];
  total_debit: string;
  total_credit: string;
  closing_balance: string;
}

export type GeneralLedgerReport = AccountLedger[];

export interface ProfitLossReport {
  revenue: AccountBalance[];
  contra_revenue: AccountBalance[];
  expenses: AccountBalance[];
  other_income: AccountBalance[];
  other_expenses: AccountBalance[];
  total_revenue: string;
  total_contra_revenue: string;
  total_expenses: string;
  total_other_income: string;
  total_other_expenses: string;
  net_profit_loss: string;
}

export interface BalanceSheetReport {
  assets: AccountBalance[];
  contra_assets: AccountBalance[];
  liabilities: AccountBalance[];
  equity: AccountBalance[];
  current_year_profit_loss: string;
  total_assets: string;
  total_liabilities: string;
  total_equity: string;
  total_liabilities_and_equity: string;
  is_balanced: boolean;
  difference: string;
}

export interface AccountingReportFilters {
  organization?: string | null;
  branch?: string | null;
  academic_year?: string | null;
  academic_period?: string | null;
  date_from?: string | null;
  date_to?: string | null;
  account?: string | null;
  include_zero_balances?: boolean;
}

export type PaginatedAccounts = PaginatedResponse<Account>;
export type PaginatedJournalEntries = PaginatedResponse<JournalEntry>;
export type PaginatedJournalEntryLines = PaginatedResponse<JournalEntryLine>;
export type PaginatedAccountingDocuments = PaginatedResponse<AccountingDocument>;
