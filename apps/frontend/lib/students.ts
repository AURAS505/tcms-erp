import { apiClient, apiClientEnvelope } from "@/lib/api-client";
import type { PaginatedResponse, Student, StudentInquiry } from "@/types/students";

const STUDENT_API_BASE = "/api/v1";

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

export function listStudentInquiries(search?: string) {
  return listResource<StudentInquiry>(buildListPath(`${STUDENT_API_BASE}/student-inquiries/`, search));
}

export function getStudentInquiry(id: string) {
  return apiClient<StudentInquiry>(`${STUDENT_API_BASE}/student-inquiries/${id}/`);
}

export function listStudents(search?: string) {
  return listResource<Student>(buildListPath(`${STUDENT_API_BASE}/students/`, search));
}

export function getStudent(id: string) {
  return apiClient<Student>(`${STUDENT_API_BASE}/students/${id}/`);
}

