export type Role =
  | "super_admin"
  | "institute_owner"
  | "branch_admin"
  | "accountant"
  | "receptionist"
  | "teacher"
  | "auditor"
  | "student_portal_user"
  | "parent_portal_user";

export interface Permission {
  id: string;
  code: string;
  name: string;
  module: string;
  isReadOnly: boolean;
}

export interface RoleSummary {
  id: string;
  code: Role;
  name: string;
  isReadOnly: boolean;
}

export interface BranchAssignment {
  id: string;
  organizationId: string;
  branchId: string;
  isPrimary: boolean;
}

export interface User {
  id: string;
  email: string;
  username: string;
  fullName: string;
  roles: RoleSummary[];
  permissions: Permission[];
  branchAssignments: BranchAssignment[];
  forcePasswordChange: boolean;
}

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

export interface LoginRequest {
  identifier: string;
  password: string;
}

export interface PasswordResetRequest {
  email: string;
}

export interface PasswordResetConfirmRequest {
  token: string;
  newPassword: string;
}

export interface ForcePasswordChangeRequest {
  currentPassword: string;
  newPassword: string;
}
