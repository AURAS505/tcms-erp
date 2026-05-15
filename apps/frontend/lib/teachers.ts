import { apiClient, apiClientEnvelope } from "@/lib/api-client";
import type { PaginatedResponse } from "@/types/students";
import type { Teacher, TeacherActivity, TeacherContract, TeacherStatusHistory } from "@/types/teachers";

const TEACHER_API_BASE = "/api/v1";

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

export function listTeachers(search?: string) {
  return listResource<Teacher>(buildListPath(`${TEACHER_API_BASE}/teachers/`, search));
}

export function getTeacher(id: string) {
  return apiClient<Teacher>(`${TEACHER_API_BASE}/teachers/${id}/`);
}

export function listTeacherContracts(search?: string) {
  return listResource<TeacherContract>(buildListPath(`${TEACHER_API_BASE}/teacher-contracts/`, search));
}

export function getTeacherContract(id: string) {
  return apiClient<TeacherContract>(`${TEACHER_API_BASE}/teacher-contracts/${id}/`);
}

export function listTeacherActivities(search?: string) {
  return listResource<TeacherActivity>(buildListPath(`${TEACHER_API_BASE}/teacher-activities/`, search));
}

export function listTeacherStatusHistory(search?: string) {
  return listResource<TeacherStatusHistory>(buildListPath(`${TEACHER_API_BASE}/teacher-status-history/`, search));
}
