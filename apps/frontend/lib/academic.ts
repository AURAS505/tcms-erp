import { apiClient, apiClientEnvelope } from "@/lib/api-client";
import type {
  AcademicYear,
  AcademicYearCloseInput,
  AcademicYearRollover,
  AcademicYearRolloverSummary,
  PaginatedAcademicRollovers,
  PaginatedAcademicYears,
  RolloverCancelInput,
  RolloverExecuteInput,
  RolloverPrepareInput,
} from "@/types/academic";

const ACADEMIC_API_BASE = "/api/v1";

function buildListPath(path: string, search?: string) {
  const params = new URLSearchParams();
  if (search) params.set("search", search);
  const query = params.toString();
  return query ? `${path}?${query}` : path;
}

async function listResource<T>(path: string) {
  const envelope = await apiClientEnvelope<T[]>(path);
  return {
    data: envelope.data,
    pagination: envelope.meta?.pagination as PaginatedAcademicYears["pagination"],
  };
}

export function listAcademicYears(search?: string): Promise<PaginatedAcademicYears> {
  return listResource<AcademicYear>(buildListPath(`${ACADEMIC_API_BASE}/academic-years/`, search));
}

export function getAcademicYear(id: string) {
  return apiClient<AcademicYear>(`${ACADEMIC_API_BASE}/academic-years/${id}/`);
}

export function softCloseAcademicYear(id: string, payload: AcademicYearCloseInput = {}) {
  return apiClient<AcademicYear>(`${ACADEMIC_API_BASE}/academic-years/${id}/soft-close/`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function hardCloseAcademicYear(id: string, payload: AcademicYearCloseInput = {}) {
  return apiClient<AcademicYear>(`${ACADEMIC_API_BASE}/academic-years/${id}/hard-close/`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function listAcademicRollovers(search?: string): Promise<PaginatedAcademicRollovers> {
  return listResource<AcademicYearRollover>(buildListPath(`${ACADEMIC_API_BASE}/academic-year-rollovers/`, search));
}

export function getAcademicRollover(id: string) {
  return apiClient<AcademicYearRollover>(`${ACADEMIC_API_BASE}/academic-year-rollovers/${id}/`);
}

export function prepareAcademicRollover(payload: RolloverPrepareInput) {
  return apiClient<AcademicYearRollover>(`${ACADEMIC_API_BASE}/academic-year-rollovers/prepare/`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function validateAcademicRollover(id: string) {
  return apiClient<AcademicYearRollover>(`${ACADEMIC_API_BASE}/academic-year-rollovers/${id}/validate/`, {
    method: "POST",
    body: "{}",
  });
}

export function executeAcademicRollover(id: string, payload: RolloverExecuteInput) {
  return apiClient<AcademicYearRollover>(`${ACADEMIC_API_BASE}/academic-year-rollovers/${id}/execute/`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function cancelAcademicRollover(id: string, payload: RolloverCancelInput = {}) {
  return apiClient<AcademicYearRollover>(`${ACADEMIC_API_BASE}/academic-year-rollovers/${id}/cancel/`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getAcademicRolloverSummary(id: string) {
  return apiClient<AcademicYearRolloverSummary>(`${ACADEMIC_API_BASE}/academic-year-rollovers/${id}/summary/`);
}
