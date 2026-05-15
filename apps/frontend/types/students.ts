import type { ApiPaginationMeta } from "@/lib/api-client";

export type StudentStatus = "inquiry" | "pending" | "active" | "on_break" | "left" | "graduated" | "rejected";

export type StudentInquiryStatus =
  | "new"
  | "contacted"
  | "appointment_scheduled"
  | "converted"
  | "closed"
  | "rejected";

export interface PaginatedResponse<T> {
  data: T[];
  pagination: ApiPaginationMeta;
}

export interface StudentInquiry {
  id: string;
  student_full_name: string;
  guardian_name: string;
  contact_number: string;
  email: string;
  interested_class_subject: string;
  inquiry_source: string;
  status: StudentInquiryStatus;
  notes: string;
  created_at: string;
  updated_at: string;
}

export interface StudentDocumentSummary {
  id: string;
  document_type: string;
  file_name: string;
}

export interface Student {
  id: string;
  admission_number: string;
  full_name: string;
  preferred_name: string;
  gender: string;
  date_of_birth_ad: string | null;
  date_of_birth_bs: string;
  phone: string;
  email: string;
  permanent_address: string;
  temporary_address: string;
  school_college_name: string;
  current_grade_class: string;
  status: StudentStatus;
  admission_date_ad: string | null;
  admission_date_bs: string;
  notes: string;
  created_at: string;
  updated_at: string;
}

