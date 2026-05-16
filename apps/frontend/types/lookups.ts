import type { PaginatedResponse } from "@/types/students";

export interface OrganizationOption {
  id: string;
  display_name: string;
  legal_name: string;
  is_active: boolean;
}

export interface BranchOption {
  id: string;
  organization: string;
  code: string;
  name: string;
  is_active: boolean;
}

export interface AcademicYearOption {
  id: string;
  organization: string;
  name: string;
  ad_start_date: string;
  ad_end_date: string;
  status: string;
  is_active: boolean;
}

export interface AcademicPeriodOption {
  id: string;
  organization: string;
  academic_year: string;
  name: string;
  ad_start_date: string;
  ad_end_date: string;
  status: string;
  is_active: boolean;
}

export type PaginatedOrganizations = PaginatedResponse<OrganizationOption>;
export type PaginatedBranches = PaginatedResponse<BranchOption>;
export type PaginatedAcademicYears = PaginatedResponse<AcademicYearOption>;
export type PaginatedAcademicPeriods = PaginatedResponse<AcademicPeriodOption>;
