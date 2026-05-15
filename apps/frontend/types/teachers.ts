import type { PaginatedResponse } from "@/types/students";

export type TeacherStatus = "pending" | "active" | "inactive" | "on_leave" | "resigned" | "terminated";
export type TeacherContractType = "monthly_cut_percentage" | "package_course" | "fixed_monthly_salary";
export type TeacherActivityStatus = "open" | "completed" | "cancelled";

export interface Teacher {
  id: string;
  organization: string;
  branch: string;
  user: string | null;
  employee_number: string;
  full_name: string;
  preferred_name: string;
  gender: string;
  date_of_birth_ad: string | null;
  date_of_birth_bs: string;
  phone: string;
  alternate_phone: string;
  email: string;
  address: string;
  qualification: string;
  specialization: string;
  experience_summary: string;
  joining_date_ad: string | null;
  joining_date_bs: string;
  photo_path: string;
  status: TeacherStatus;
  notes: string;
  created_at: string;
  updated_at: string;
}

export interface TeacherContract {
  id: string;
  teacher: string;
  organization: string;
  branch: string;
  academic_year: string | null;
  contract_type: TeacherContractType;
  default_teacher_cut_percentage: string | null;
  package_amount: string | null;
  fixed_monthly_salary: string | null;
  effective_from_ad: string;
  effective_from_bs: string;
  effective_to_ad: string | null;
  effective_to_bs: string;
  is_active: boolean;
  notes: string;
  created_at: string;
  updated_at: string;
}

export interface TeacherActivity {
  id: string;
  teacher: string;
  organization: string;
  branch: string;
  academic_year: string | null;
  activity_type: string;
  title: string;
  description: string;
  activity_date_ad: string | null;
  activity_date_bs: string;
  status: TeacherActivityStatus;
  created_by: string | null;
  created_at: string;
  updated_at: string;
}

export interface TeacherStatusHistory {
  id: string;
  teacher: string;
  from_status: TeacherStatus | "";
  to_status: TeacherStatus;
  reason: string;
  changed_by: string | null;
  changed_at: string;
  metadata: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
}

export type PaginatedTeachers = PaginatedResponse<Teacher>;
export type PaginatedTeacherContracts = PaginatedResponse<TeacherContract>;
export type PaginatedTeacherActivities = PaginatedResponse<TeacherActivity>;
export type PaginatedTeacherStatusHistory = PaginatedResponse<TeacherStatusHistory>;
