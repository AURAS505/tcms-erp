import type { PaginatedResponse } from "@/types/students";

export type ClassStatus = "draft" | "active" | "paused" | "completed" | "cancelled";
export type EnrollmentStatus = "active" | "on_break" | "completed" | "left" | "cancelled";
export type ReviewStatus = "draft" | "pending" | "pending_approval" | "pending_review" | "approved" | "rejected" | "active" | "completed" | "cancelled";

export interface Subject {
  id: string;
  subject_code: string;
  subject_name: string;
  description: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ClassRoom {
  id: string;
  class_name: string;
  batch_name: string;
  section_name: string;
  primary_teacher: string | null;
  subjects: string[];
  start_date_ad: string | null;
  start_date_bs: string;
  expected_end_date_ad: string | null;
  expected_end_date_bs: string;
  capacity: number | null;
  monthly_fee: string | null;
  teacher_cut_percentage: string | null;
  teacher_payment_type: string;
  payment_due_rule: string;
  due_day: number | null;
  status: ClassStatus;
  notes: string;
  created_at: string;
  updated_at: string;
}

export interface ClassSchedule {
  id: string;
  class_room: string;
  day_of_week: string;
  start_time: string;
  end_time: string;
  room_name: string;
  is_active: boolean;
  notes: string;
  created_at: string;
  updated_at: string;
}

export interface ClassEnrollment {
  id: string;
  organization: string;
  branch: string;
  academic_year: string | null;
  student: string;
  class_room: string;
  joined_date_ad: string | null;
  joined_date_bs: string;
  end_date_ad: string | null;
  end_date_bs: string;
  left_date_ad: string | null;
  left_date_bs: string;
  status: EnrollmentStatus;
  enrollment_discount_percentage: string | null;
  enrollment_discount_amount: string | null;
  teacher_cut_percentage_override: string | null;
  notes: string;
  created_at: string;
  updated_at: string;
}

export interface ClassEnrollmentBreak {
  id: string;
  enrollment: string;
  break_start_date_ad: string | null;
  break_start_date_bs: string;
  expected_return_date_ad: string | null;
  expected_return_date_bs: string;
  actual_return_date_ad: string | null;
  actual_return_date_bs: string;
  reason: string;
  status: ReviewStatus;
  approved_by: string | null;
  approved_at: string | null;
  notes: string;
  created_at: string;
  updated_at: string;
}

export interface ClassEnrollmentDiscount {
  id: string;
  enrollment: string;
  discount_type: string;
  discount_percentage: string | null;
  discount_amount: string | null;
  effective_from_ad: string | null;
  effective_from_bs: string;
  effective_to_ad: string | null;
  effective_to_bs: string;
  reason: string;
  status: ReviewStatus;
  approved_by: string | null;
  approved_at: string | null;
  notes: string;
  created_at: string;
  updated_at: string;
}

export interface StudentWithdrawal {
  id: string;
  enrollment: string;
  student: string;
  organization: string;
  branch: string;
  academic_year: string | null;
  last_attendance_date_ad: string | null;
  last_attendance_date_bs: string;
  reason: string;
  status: ReviewStatus;
  reviewed_by: string | null;
  approved_by: string | null;
  approved_at: string | null;
  notes: string;
  created_at: string;
  updated_at: string;
}

export interface ClassTeacherTransfer {
  id: string;
  class_room: string;
  from_teacher: string | null;
  to_teacher: string;
  effective_date_ad: string | null;
  effective_date_bs: string;
  reason: string;
  status: ReviewStatus;
  approved_by: string | null;
  approved_at: string | null;
  notes: string;
  created_at: string;
  updated_at: string;
}

export type PaginatedSubjects = PaginatedResponse<Subject>;
export type PaginatedClasses = PaginatedResponse<ClassRoom>;
export type PaginatedClassSchedules = PaginatedResponse<ClassSchedule>;
export type PaginatedClassEnrollments = PaginatedResponse<ClassEnrollment>;
export type PaginatedEnrollmentBreaks = PaginatedResponse<ClassEnrollmentBreak>;
export type PaginatedEnrollmentDiscounts = PaginatedResponse<ClassEnrollmentDiscount>;
export type PaginatedStudentWithdrawals = PaginatedResponse<StudentWithdrawal>;
export type PaginatedTeacherTransfers = PaginatedResponse<ClassTeacherTransfer>;
