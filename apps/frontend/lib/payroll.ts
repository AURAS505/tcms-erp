import { apiClient, apiClientEnvelope } from "@/lib/api-client";
import type { PaginatedResponse } from "@/types/students";
import type {
  TeacherDeduction,
  TeacherEarning,
  TeacherEarningApproveInput,
  TeacherEarningCreateInput,
  TeacherEarningListFilters,
  TeacherPayment,
  TeacherPaymentApproveInput,
  TeacherPaymentAllocation,
  TeacherPaymentBatch,
  TeacherPaymentDraftCreateInput,
  TeacherPaymentVoidPlaceholderInput,
} from "@/types/payroll";

const PAYROLL_API_BASE = "/api/v1";

function buildListPath(path: string, filters?: string | TeacherEarningListFilters) {
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

export function listTeacherEarnings(filters?: string | TeacherEarningListFilters) {
  return listResource<TeacherEarning>(buildListPath(`${PAYROLL_API_BASE}/teacher-earnings/`, filters));
}

export function getTeacherEarning(id: string) {
  return apiClient<TeacherEarning>(`${PAYROLL_API_BASE}/teacher-earnings/${id}/`);
}

export function createManualTeacherEarning(payload: TeacherEarningCreateInput) {
  return apiClient<TeacherEarning>(`${PAYROLL_API_BASE}/teacher-earnings/create-manual/`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function approveTeacherEarning(id: string, payload: TeacherEarningApproveInput = {}) {
  return apiClient<TeacherEarning>(`${PAYROLL_API_BASE}/teacher-earnings/${id}/approve/`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function postTeacherEarning(id: string, payload: TeacherEarningApproveInput = {}) {
  return apiClient<TeacherEarning>(`${PAYROLL_API_BASE}/teacher-earnings/${id}/post/`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function listTeacherPaymentBatches(search?: string) {
  return listResource<TeacherPaymentBatch>(buildListPath(`${PAYROLL_API_BASE}/teacher-payment-batches/`, search));
}

export function getTeacherPaymentBatch(id: string) {
  return apiClient<TeacherPaymentBatch>(`${PAYROLL_API_BASE}/teacher-payment-batches/${id}/`);
}

export function listTeacherPayments(search?: string) {
  return listResource<TeacherPayment>(buildListPath(`${PAYROLL_API_BASE}/teacher-payments/`, search));
}

export function getTeacherPayment(id: string) {
  return apiClient<TeacherPayment>(`${PAYROLL_API_BASE}/teacher-payments/${id}/`);
}

export function createDraftTeacherPayment(payload: TeacherPaymentDraftCreateInput) {
  return apiClient<TeacherPayment>(`${PAYROLL_API_BASE}/teacher-payments/create-draft/`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function approveTeacherPayment(id: string, payload: TeacherPaymentApproveInput = {}) {
  return apiClient<TeacherPayment>(`${PAYROLL_API_BASE}/teacher-payments/${id}/approve/`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function postTeacherPayment(id: string, payload: TeacherPaymentApproveInput = {}) {
  return apiClient<TeacherPayment>(`${PAYROLL_API_BASE}/teacher-payments/${id}/post/`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function voidTeacherPaymentPlaceholder(id: string, payload: TeacherPaymentVoidPlaceholderInput) {
  return apiClient<TeacherPayment>(`${PAYROLL_API_BASE}/teacher-payments/${id}/void-placeholder/`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function listTeacherPaymentAllocations(search?: string) {
  return listResource<TeacherPaymentAllocation>(
    buildListPath(`${PAYROLL_API_BASE}/teacher-payment-allocations/`, search),
  );
}

export function listTeacherDeductions(search?: string) {
  return listResource<TeacherDeduction>(buildListPath(`${PAYROLL_API_BASE}/teacher-deductions/`, search));
}
