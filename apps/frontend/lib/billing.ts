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

function buildListPath(path: string, search?: string) {
  const params = new URLSearchParams();
  if (search) params.set("search", search);
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

export function listFeeDues(search?: string) {
  return listResource<StudentFeeDue>(buildListPath(`${BILLING_API_BASE}/student-fee-dues/`, search));
}

export function getFeeDue(id: string) {
  return apiClient<StudentFeeDue>(`${BILLING_API_BASE}/student-fee-dues/${id}/`);
}

export function listInvoices(search?: string) {
  return listResource<StudentInvoice>(buildListPath(`${BILLING_API_BASE}/student-invoices/`, search));
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
