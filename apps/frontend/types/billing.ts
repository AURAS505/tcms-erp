import type { PaginatedResponse } from "@/types/students";

export type BillStatus =
  | "draft"
  | "pending_approval"
  | "approved"
  | "unpaid"
  | "partial"
  | "paid"
  | "cancelled"
  | "written_off";

export type PaymentStatus = "draft" | "submitted" | "approved" | "posted" | "voided" | "refunded";
export type AdjustmentStatus = "draft" | "pending_approval" | "approved" | "rejected" | "cancelled";
export type FineStatus = "draft" | "pending_approval" | "approved" | "waived" | "cancelled";
export type RefundStatus = "draft" | "pending_approval" | "approved" | "paid" | "cancelled";

export interface FeePlan {
  id: string;
  organization: string;
  branch: string;
  academic_year: string;
  class_room: string | null;
  name: string;
  fee_plan_type: string;
  billing_frequency: string;
  payment_due_rule: string;
  due_day: number | null;
  is_active: boolean;
  notes: string;
  created_at: string;
  updated_at: string;
}

export interface FeePlanItem {
  id: string;
  fee_plan: string;
  item_name: string;
  fee_type: string;
  amount: string;
  is_recurring: boolean;
  sort_order: number;
  notes: string;
  created_at: string;
  updated_at: string;
}

export interface StudentFeeDue {
  id: string;
  organization: string;
  branch: string;
  academic_year: string;
  academic_period: string | null;
  student: string;
  class_room: string | null;
  class_enrollment: string | null;
  fee_plan: string | null;
  period_label: string;
  due_date_ad: string | null;
  due_date_bs: string;
  original_amount: string;
  discount_amount: string;
  fine_amount: string;
  net_amount: string;
  paid_amount: string;
  balance_amount: string;
  status: BillStatus;
  approved_by: string | null;
  approved_at: string | null;
  cancelled_by: string | null;
  cancelled_at: string | null;
  cancellation_reason: string;
  notes: string;
  created_at: string;
  updated_at: string;
}

export interface StudentInvoice {
  id: string;
  organization: string;
  branch: string;
  academic_year: string;
  academic_period: string | null;
  student: string;
  invoice_number: string;
  invoice_date_ad: string;
  invoice_date_bs: string;
  due_date_ad: string | null;
  due_date_bs: string;
  subtotal: string;
  discount_amount: string;
  fine_amount: string;
  total_amount: string;
  paid_amount: string;
  balance_amount: string;
  status: BillStatus;
  notes: string;
  created_at: string;
  updated_at: string;
}

export interface StudentInvoiceItem {
  id: string;
  invoice: string;
  fee_due: string | null;
  description: string;
  fee_type: string;
  quantity: string;
  unit_amount: string;
  discount_amount: string;
  fine_amount: string;
  line_total: string;
  notes: string;
  created_at: string;
  updated_at: string;
}

export interface StudentPayment {
  id: string;
  organization: string;
  branch: string;
  academic_year: string;
  student: string;
  receipt_number: string | null;
  draft_receipt_number: string | null;
  payment_date_ad: string;
  payment_date_bs: string;
  payment_method: string;
  amount: string;
  discount_amount: string;
  fine_amount: string;
  net_received_amount: string;
  reference_number: string;
  file_path: string;
  is_advance_payment: boolean;
  status: PaymentStatus;
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

export interface StudentPaymentAllocation {
  id: string;
  payment: string;
  fee_due: string | null;
  invoice: string | null;
  invoice_item: string | null;
  amount_allocated: string;
  notes: string;
  created_at: string;
  updated_at: string;
}

export interface StudentPaymentAllocationInput {
  fee_due?: string;
  invoice?: string;
  invoice_item?: string;
  amount_allocated: string;
  notes?: string;
}

export interface StudentPaymentDraftCreateInput {
  organization: string;
  branch: string;
  academic_year: string;
  student: string;
  payment_date_ad: string;
  payment_date_bs?: string;
  payment_method: string;
  amount: string;
  discount_amount?: string;
  fine_amount?: string;
  net_received_amount?: string | null;
  is_advance_payment?: boolean;
  reference_number?: string;
  file_path?: string;
  notes?: string;
  allocations?: StudentPaymentAllocationInput[];
}

export interface StudentPaymentApproveInput {
  notes?: string;
}

export interface StudentPaymentVoidPlaceholderInput {
  reason: string;
}

export interface StudentAdvanceBalance {
  id: string;
  organization: string;
  branch: string;
  academic_year: string;
  student: string;
  opening_amount: string;
  received_amount: string;
  applied_amount: string;
  refunded_amount: string;
  balance_amount: string;
  notes: string;
  created_at: string;
  updated_at: string;
}

export interface BillingDiscount {
  id: string;
  organization: string;
  branch: string;
  academic_year: string;
  student: string;
  class_enrollment: string | null;
  fee_due: string | null;
  invoice: string | null;
  discount_type: string;
  discount_percentage: string | null;
  discount_amount: string | null;
  reason: string;
  status: AdjustmentStatus;
  approved_by: string | null;
  approved_at: string | null;
  notes: string;
  created_at: string;
  updated_at: string;
}

export interface BillingWaiver {
  id: string;
  organization: string;
  branch: string;
  academic_year: string;
  student: string;
  fee_due: string | null;
  invoice: string | null;
  waiver_amount: string;
  reason: string;
  status: AdjustmentStatus;
  approved_by: string | null;
  approved_at: string | null;
  notes: string;
  created_at: string;
  updated_at: string;
}

export interface BillingFine {
  id: string;
  organization: string;
  branch: string;
  academic_year: string;
  student: string;
  fee_due: string | null;
  invoice: string | null;
  fine_type: string;
  amount: string;
  reason: string;
  status: FineStatus;
  approved_by: string | null;
  approved_at: string | null;
  notes: string;
  created_at: string;
  updated_at: string;
}

export interface StudentRefund {
  id: string;
  organization: string;
  branch: string;
  academic_year: string;
  student: string;
  original_payment: string | null;
  refund_voucher_number: string | null;
  refund_date_ad: string | null;
  refund_date_bs: string;
  refund_amount: string;
  refund_reason: string;
  status: RefundStatus;
  requested_by: string | null;
  approved_by: string | null;
  approved_at: string | null;
  paid_by: string | null;
  paid_at: string | null;
  notes: string;
  created_at: string;
  updated_at: string;
}

export type PaginatedFeePlans = PaginatedResponse<FeePlan>;
export type PaginatedFeePlanItems = PaginatedResponse<FeePlanItem>;
export type PaginatedFeeDues = PaginatedResponse<StudentFeeDue>;
export type PaginatedInvoices = PaginatedResponse<StudentInvoice>;
export type PaginatedInvoiceItems = PaginatedResponse<StudentInvoiceItem>;
export type PaginatedStudentPayments = PaginatedResponse<StudentPayment>;
export type PaginatedPaymentAllocations = PaginatedResponse<StudentPaymentAllocation>;
export type PaginatedAdvanceBalances = PaginatedResponse<StudentAdvanceBalance>;
export type PaginatedBillingDiscounts = PaginatedResponse<BillingDiscount>;
export type PaginatedBillingWaivers = PaginatedResponse<BillingWaiver>;
export type PaginatedBillingFines = PaginatedResponse<BillingFine>;
export type PaginatedStudentRefunds = PaginatedResponse<StudentRefund>;
