import { apiClient, apiClientEnvelope } from "@/lib/api-client";
import type {
  ClassEnrollment,
  ClassEnrollmentBreak,
  ClassEnrollmentDiscount,
  ClassRoom,
  ClassSchedule,
  ClassTeacherTransfer,
  StudentWithdrawal,
  Subject,
} from "@/types/classes";
import type { PaginatedResponse } from "@/types/students";

const CLASS_API_BASE = "/api/v1";

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

export function listSubjects(search?: string) {
  return listResource<Subject>(buildListPath(`${CLASS_API_BASE}/subjects/`, search));
}

export function getSubject(id: string) {
  return apiClient<Subject>(`${CLASS_API_BASE}/subjects/${id}/`);
}

export function listClasses(search?: string) {
  return listResource<ClassRoom>(buildListPath(`${CLASS_API_BASE}/classes/`, search));
}

export function getClass(id: string) {
  return apiClient<ClassRoom>(`${CLASS_API_BASE}/classes/${id}/`);
}

export function listClassSchedules(search?: string) {
  return listResource<ClassSchedule>(buildListPath(`${CLASS_API_BASE}/class-schedules/`, search));
}

export function listClassEnrollments(search?: string) {
  return listResource<ClassEnrollment>(buildListPath(`${CLASS_API_BASE}/class-enrollments/`, search));
}

export function getClassEnrollment(id: string) {
  return apiClient<ClassEnrollment>(`${CLASS_API_BASE}/class-enrollments/${id}/`);
}

export function listEnrollmentBreaks(search?: string) {
  return listResource<ClassEnrollmentBreak>(buildListPath(`${CLASS_API_BASE}/class-enrollment-breaks/`, search));
}

export function listEnrollmentDiscounts(search?: string) {
  return listResource<ClassEnrollmentDiscount>(
    buildListPath(`${CLASS_API_BASE}/class-enrollment-discounts/`, search),
  );
}

export function listStudentWithdrawals(search?: string) {
  return listResource<StudentWithdrawal>(buildListPath(`${CLASS_API_BASE}/student-withdrawals/`, search));
}

export function listTeacherTransfers(search?: string) {
  return listResource<ClassTeacherTransfer>(buildListPath(`${CLASS_API_BASE}/class-teacher-transfers/`, search));
}
