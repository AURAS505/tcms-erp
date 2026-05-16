import { apiClient, apiClientEnvelope } from "@/lib/api-client";
import type {
  BillingDiscount,
  BillingFine,
  BillingWaiver,
  FeePlan,
  StudentAdvanceBalance,
  StudentFeeDue,
  StudentInvoice,
  StudentPayment,
  StudentPaymentApproveInput,
  StudentPaymentDraftCreateInput,
  StudentPaymentVoidPlaceholderInput,
  StudentRefund,
} from "@/types/billing";
import type { PaginatedResponse } from "@/types/students";

const BILLING_API_BASE = "/api/v1";

export interface BillingListFilters {
  search?: string;
  organization?: string;
  branch?: string;
  academic_year?: string;
  academic_period?: string;
  student?: string;
  status?: string;
  open_only?: boolean | string;
}

function buildListPath(path: string, filters?: string | BillingListFilters) {
  const params = new URLSearchParams();
  if (typeof filters === "string") {
    if (filters) params.set("search", filters);
  } else if (filters) {
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== "") params.set(key, String(value));
    });
  }
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

export function listFeePlans(search?: string) {
  return listResource<FeePlan>(buildListPath(`${BILLING_API_BASE}/fee-plans/`, search));
}

export function getFeePlan(id: string) {
  return apiClient<FeePlan>(`${BILLING_API_BASE}/fee-plans/${id}/`);
}

export function listFeeDues(filters?: string | BillingListFilters) {
  return listResource<StudentFeeDue>(buildListPath(`${BILLING_API_BASE}/student-fee-dues/`, filters));
}

export function getFeeDue(id: string) {
  return apiClient<StudentFeeDue>(`${BILLING_API_BASE}/student-fee-dues/${id}/`);
}

export function listInvoices(filters?: string | BillingListFilters) {
  return listResource<StudentInvoice>(buildListPath(`${BILLING_API_BASE}/student-invoices/`, filters));
}

export function getInvoice(id: string) {
  return apiClient<StudentInvoice>(`${BILLING_API_BASE}/student-invoices/${id}/`);
}

export function listStudentPayments(search?: string) {
  return listResource<StudentPayment>(buildListPath(`${BILLING_API_BASE}/student-payments/`, search));
}

export function getStudentPayment(id: string) {
  return apiClient<StudentPayment>(`${BILLING_API_BASE}/student-payments/${id}/`);
}

export function createDraftStudentPayment(payload: StudentPaymentDraftCreateInput) {
  return apiClient<StudentPayment>(`${BILLING_API_BASE}/student-payments/create-draft/`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function approveStudentPayment(id: string, payload: StudentPaymentApproveInput = {}) {
  return apiClient<StudentPayment>(`${BILLING_API_BASE}/student-payments/${id}/approve/`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function voidStudentPaymentPlaceholder(id: string, payload: StudentPaymentVoidPlaceholderInput) {
  return apiClient<StudentPayment>(`${BILLING_API_BASE}/student-payments/${id}/void-placeholder/`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function listAdvanceBalances(search?: string) {
  return listResource<StudentAdvanceBalance>(buildListPath(`${BILLING_API_BASE}/student-advance-balances/`, search));
}

export function listBillingDiscounts(search?: string) {
  return listResource<BillingDiscount>(buildListPath(`${BILLING_API_BASE}/billing-discounts/`, search));
}

export function listBillingWaivers(search?: string) {
  return listResource<BillingWaiver>(buildListPath(`${BILLING_API_BASE}/billing-waivers/`, search));
}

export function listBillingFines(search?: string) {
  return listResource<BillingFine>(buildListPath(`${BILLING_API_BASE}/billing-fines/`, search));
}

export function listStudentRefunds(search?: string) {
  return listResource<StudentRefund>(buildListPath(`${BILLING_API_BASE}/student-refunds/`, search));
}
