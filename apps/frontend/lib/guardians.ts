import { apiClient, apiClientEnvelope } from "@/lib/api-client";
import type { PaginatedResponse } from "@/types/students";
import type { Family, Guardian, StudentGuardian } from "@/types/guardians";

const GUARDIAN_API_BASE = "/api/v1";

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

export function listFamilies(search?: string) {
  return listResource<Family>(buildListPath(`${GUARDIAN_API_BASE}/families/`, search));
}

export function getFamily(id: string) {
  return apiClient<Family>(`${GUARDIAN_API_BASE}/families/${id}/`);
}

export function listGuardians(search?: string) {
  return listResource<Guardian>(buildListPath(`${GUARDIAN_API_BASE}/guardians/`, search));
}

export function getGuardian(id: string) {
  return apiClient<Guardian>(`${GUARDIAN_API_BASE}/guardians/${id}/`);
}

export function listStudentGuardians(search?: string) {
  return listResource<StudentGuardian>(buildListPath(`${GUARDIAN_API_BASE}/student-guardians/`, search));
}

