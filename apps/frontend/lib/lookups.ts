import { apiClientEnvelope } from "@/lib/api-client";
import type { PaginatedResponse } from "@/types/students";
import type { AcademicPeriodOption, AcademicYearOption, BranchOption, OrganizationOption } from "@/types/lookups";

const LOOKUP_API_BASE = "/api/v1";

async function listResource<T>(path: string): Promise<PaginatedResponse<T>> {
  const envelope = await apiClientEnvelope<T[]>(path);
  return {
    data: envelope.data,
    pagination: envelope.meta?.pagination as PaginatedResponse<T>["pagination"],
  };
}

export function listOrganizations() {
  return listResource<OrganizationOption>(`${LOOKUP_API_BASE}/organizations/`);
}

export function listBranches() {
  return listResource<BranchOption>(`${LOOKUP_API_BASE}/branches/`);
}

export function listAcademicYears() {
  return listResource<AcademicYearOption>(`${LOOKUP_API_BASE}/academic-years/`);
}

export function listAcademicPeriods() {
  return listResource<AcademicPeriodOption>(`${LOOKUP_API_BASE}/academic-periods/`);
}
