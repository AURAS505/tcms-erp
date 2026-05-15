import type { PaginatedResponse } from "@/types/students";

export type GuardianStatus = "active" | "inactive";

export interface Family {
  id: string;
  family_code: string;
  primary_contact_name: string;
  primary_contact_number: string;
  address: string;
  notes: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Guardian {
  id: string;
  family: string | null;
  full_name: string;
  relationship_type: string;
  phone: string;
  alternate_phone: string;
  email: string;
  occupation: string;
  address: string;
  is_primary_contact: boolean;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface StudentGuardian {
  id: string;
  student: string;
  guardian: string;
  relationship_type: string;
  is_primary: boolean;
  can_receive_notifications: boolean;
  can_make_payments: boolean;
  can_request_refunds: boolean;
  notes: string;
  created_at: string;
  updated_at: string;
}

export type PaginatedFamilies = PaginatedResponse<Family>;
export type PaginatedGuardians = PaginatedResponse<Guardian>;
export type PaginatedStudentGuardians = PaginatedResponse<StudentGuardian>;

