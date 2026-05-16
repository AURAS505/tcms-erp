import { apiClient, apiClientEnvelope } from "@/lib/api-client";
import type { PaginatedResponse } from "@/types/students";
import type {
  TeacherDeduction,
  TeacherEarning,
  TeacherPayment,
  TeacherPaymentAllocation,
  TeacherPaymentBatch,
} from "@/types/payroll";

const PAYROLL_API_BASE = "/api/v1";

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

export function listTeacherEarnings(search?: string) {
  return listResource<TeacherEarning>(buildListPath(`${PAYROLL_API_BASE}/teacher-earnings/`, search));
}

export function getTeacherEarning(id: string) {
  return apiClient<TeacherEarning>(`${PAYROLL_API_BASE}/teacher-earnings/${id}/`);
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

export function listTeacherPaymentAllocations(search?: string) {
  return listResource<TeacherPaymentAllocation>(
    buildListPath(`${PAYROLL_API_BASE}/teacher-payment-allocations/`, search),
  );
}

export function listTeacherDeductions(search?: string) {
  return listResource<TeacherDeduction>(buildListPath(`${PAYROLL_API_BASE}/teacher-deductions/`, search));
}
