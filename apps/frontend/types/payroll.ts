import type { PaginatedResponse } from "@/types/students";

export type TeacherEarningStatus =
  | "draft"
  | "pending_approval"
  | "approved"
  | "posted"
  | "partial"
  | "paid"
  | "cancelled"
  | "reversed";
export type TeacherPaymentBatchStatus = "draft" | "pending_approval" | "approved" | "posted" | "cancelled";
export type TeacherPaymentStatus = "draft" | "submitted" | "approved" | "posted" | "voided";
export type TeacherDeductionStatus = "draft" | "pending_approval" | "approved" | "cancelled";

export interface TeacherEarning {
  id: string;
  organization: string;
  branch: string;
  academic_year: string;
  academic_period: string | null;
  teacher: string;
  student: string | null;
  class_room: string | null;
  class_enrollment: string | null;
  student_payment: string | null;
  earning_source: string;
  earning_date_ad: string;
  earning_date_bs: string;
  period_label: string;
  gross_amount: string;
  deduction_amount: string;
  net_amount: string;
  paid_amount: string;
  balance_amount: string;
  status: TeacherEarningStatus;
  created_by: string | null;
  approved_by: string | null;
  approved_at: string | null;
  posted_at: string | null;
  notes: string;
  created_at: string;
  updated_at: string;
}

export interface TeacherPaymentBatch {
  id: string;
  organization: string;
  branch: string;
  academic_year: string;
  academic_period: string | null;
  batch_number: string;
  batch_date_ad: string;
  batch_date_bs: string;
  description: string;
  total_amount: string;
  status: TeacherPaymentBatchStatus;
  created_by: string | null;
  approved_by: string | null;
  approved_at: string | null;
  posted_at: string | null;
  notes: string;
  created_at: string;
  updated_at: string;
}

export interface TeacherPayment {
  id: string;
  organization: string;
  branch: string;
  academic_year: string;
  academic_period: string | null;
  payment_batch: string | null;
  teacher: string;
  voucher_number: string | null;
  draft_voucher_number: string | null;
  payment_date_ad: string;
  payment_date_bs: string;
  payment_method: string;
  amount: string;
  deduction_amount: string;
  net_paid_amount: string;
  reference_number: string;
  acknowledgement_file_path: string;
  status: TeacherPaymentStatus;
  created_by: string | null;
  approved_by: string | null;
  approved_at: string | null;
  posted_at: string | null;
  voided_by: string | null;
  voided_at: string | null;
  void_reason: string;
  notes: string;
  created_at: string;
  updated_at: string;
}

export interface TeacherPaymentAllocation {
  id: string;
  teacher_payment: string;
  teacher_earning: string;
  amount_allocated: string;
  notes: string;
  created_at: string;
  updated_at: string;
}

export interface TeacherDeduction {
  id: string;
  organization: string;
  branch: string;
  academic_year: string;
  teacher: string;
  teacher_earning: string | null;
  teacher_payment: string | null;
  deduction_type: string;
  amount: string;
  reason: string;
  status: TeacherDeductionStatus;
  approved_by: string | null;
  approved_at: string | null;
  notes: string;
  created_at: string;
  updated_at: string;
}

export type PaginatedTeacherEarnings = PaginatedResponse<TeacherEarning>;
export type PaginatedTeacherPaymentBatches = PaginatedResponse<TeacherPaymentBatch>;
export type PaginatedTeacherPayments = PaginatedResponse<TeacherPayment>;
export type PaginatedTeacherPaymentAllocations = PaginatedResponse<TeacherPaymentAllocation>;
export type PaginatedTeacherDeductions = PaginatedResponse<TeacherDeduction>;
