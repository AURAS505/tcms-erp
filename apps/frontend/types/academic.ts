import type { PaginatedResponse } from "@/types/students";

export type AcademicYearStatus = "draft" | "active" | "soft_closed" | "hard_closed" | "archived";
export type AcademicRolloverStatus = "draft" | "validating" | "ready" | "executed" | "failed" | "cancelled";

export interface AcademicYear {
  id: string;
  organization: string;
  name: string;
  bs_start_year: number;
  bs_end_year: number;
  bs_start_date: string;
  bs_end_date: string;
  ad_start_date: string;
  ad_end_date: string;
  status: AcademicYearStatus;
  is_active: boolean;
  notes: string;
  created_at: string;
  updated_at: string;
}

export interface AcademicYearRollover {
  id: string;
  organization: string;
  from_academic_year: string;
  to_academic_year: string | null;
  status: AcademicRolloverStatus;
  trial_balance_validated: boolean;
  revenue_expense_closing_completed: boolean;
  opening_balances_posted: boolean;
  executed_by: string | null;
  executed_at: string | null;
  notes: string;
  created_at: string;
  updated_at: string;
}

export interface AcademicYearRolloverSummary {
  id: string;
  organization: string;
  from_academic_year: string;
  to_academic_year: string | null;
  status: AcademicRolloverStatus;
  trial_balance_validated: boolean;
  revenue_expense_closing_completed: boolean;
  opening_balances_posted: boolean;
  executed_at: string | null;
}

export interface RolloverPrepareInput {
  organization: string;
  from_academic_year: string;
  notes?: string;
}

export type RolloverValidateInput = Record<string, never>;

export interface RolloverNewAcademicYearInput {
  name: string;
  bs_start_year: number;
  bs_end_year: number;
  bs_start_date: string;
  bs_end_date: string;
  ad_start_date: string;
  ad_end_date: string;
  notes?: string;
}

export interface RolloverExecuteInput {
  new_year_data?: RolloverNewAcademicYearInput;
  hard_close?: boolean;
}

export interface RolloverCancelInput {
  reason?: string;
}

export interface AcademicYearCloseInput {
  reason?: string;
}

export type PaginatedAcademicYears = PaginatedResponse<AcademicYear>;
export type PaginatedAcademicRollovers = PaginatedResponse<AcademicYearRollover>;
