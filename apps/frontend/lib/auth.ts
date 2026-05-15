import { apiClient } from "@/lib/api-client";
import type {
  ForcePasswordChangeRequest,
  LoginRequest,
  PasswordResetConfirmRequest,
  PasswordResetRequest,
  Role,
  User,
} from "@/types/auth";

const AUTH_BASE = "/api/v1/auth";

interface BackendUser {
  id: string;
  username: string;
  email: string;
  full_name: string;
  force_password_change: boolean;
  roles: Array<{ id: string; code: Role; name: string; is_read_only: boolean }>;
  permissions: Array<{ id: string; code: string; name: string; module: string; is_read_only: boolean }>;
  branch_assignments: Array<{ id: string; organization_id: string; branch_id: string; is_primary: boolean }>;
}

const normalizeUser = (user: BackendUser): User => ({
  id: user.id,
  username: user.username,
  email: user.email,
  fullName: user.full_name || user.email,
  forcePasswordChange: user.force_password_change,
  roles: user.roles.map((role) => ({
    id: role.id,
    code: role.code,
    name: role.name,
    isReadOnly: role.is_read_only,
  })),
  permissions: user.permissions.map((permission) => ({
    id: permission.id,
    code: permission.code,
    name: permission.name,
    module: permission.module,
    isReadOnly: permission.is_read_only,
  })),
  branchAssignments: user.branch_assignments.map((assignment) => ({
    id: assignment.id,
    organizationId: assignment.organization_id,
    branchId: assignment.branch_id,
    isPrimary: assignment.is_primary,
  })),
});

export const authService = {
  async login(payload: LoginRequest) {
    const user = await apiClient<BackendUser>(`${AUTH_BASE}/login/`, {
      method: "POST",
      body: JSON.stringify({
        username_or_email: payload.identifier,
        password: payload.password,
      }),
    });
    return normalizeUser(user);
  },

  logout() {
    return apiClient<null>(`${AUTH_BASE}/logout/`, { method: "POST" });
  },

  async currentUser() {
    const user = await apiClient<BackendUser>(`${AUTH_BASE}/me/`);
    return normalizeUser(user);
  },

  async checkSession() {
    const session = await apiClient<{ authenticated: boolean; user: BackendUser | null }>(`${AUTH_BASE}/session/`);
    return {
      authenticated: session.authenticated,
      user: session.user ? normalizeUser(session.user) : null,
    };
  },

  requestPasswordReset(payload: PasswordResetRequest) {
    return apiClient<{ detail?: string }>(`${AUTH_BASE}/password-reset/request/`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  confirmPasswordReset(payload: PasswordResetConfirmRequest) {
    return apiClient<{ detail?: string }>(`${AUTH_BASE}/password-reset/confirm/`, {
      method: "POST",
      body: JSON.stringify({ token: payload.token, new_password: payload.newPassword }),
    });
  },

  async forcePasswordChange(payload: ForcePasswordChangeRequest) {
    const user = await apiClient<BackendUser>(`${AUTH_BASE}/force-password-change/`, {
      method: "POST",
      body: JSON.stringify({
        current_password: payload.currentPassword,
        new_password: payload.newPassword,
      }),
    });
    return normalizeUser(user);
  },
};
