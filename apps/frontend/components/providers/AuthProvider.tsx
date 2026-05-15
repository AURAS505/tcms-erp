"use client";

import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  type ReactNode,
} from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { authService } from "@/lib/auth";
import type { BranchAssignment, LoginRequest, Permission, Role, User } from "@/types/auth";

const AUTH_QUERY_KEY = ["auth", "current-user"] as const;

interface AuthContextValue {
  branchAssignments: BranchAssignment[];
  error: Error | null;
  hasPermission: (permissionCode: string) => boolean;
  hasRole: (role: Role) => boolean;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (payload: LoginRequest) => Promise<User>;
  logout: () => Promise<void>;
  permissions: Permission[];
  refreshSession: () => Promise<User | null>;
  user: User | null;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient();
  const {
    data: user = null,
    error,
    isLoading,
    refetch,
  } = useQuery({
    queryKey: AUTH_QUERY_KEY,
    queryFn: authService.currentUser,
    retry: false,
  });

  const login = useCallback(
    async (payload: LoginRequest) => {
      const nextUser = await authService.login(payload);
      queryClient.setQueryData(AUTH_QUERY_KEY, nextUser);
      return nextUser;
    },
    [queryClient],
  );

  const logout = useCallback(async () => {
    try {
      await authService.logout();
    } finally {
      queryClient.setQueryData(AUTH_QUERY_KEY, null);
    }
  }, [queryClient]);

  const refreshSession = useCallback(async () => {
    const result = await refetch();
    return result.data ?? null;
  }, [refetch]);

  const value = useMemo<AuthContextValue>(() => {
    const roles = user?.roles.map((role) => role.code) ?? [];
    const permissions = user?.permissions ?? [];

    return {
      branchAssignments: user?.branchAssignments ?? [],
      error: error instanceof Error ? error : null,
      hasPermission: (permissionCode: string) => permissions.some((permission) => permission.code === permissionCode),
      hasRole: (role: Role) => roles.includes(role),
      isAuthenticated: Boolean(user),
      isLoading,
      login,
      logout,
      permissions,
      refreshSession,
      user,
    };
  }, [error, isLoading, login, logout, refreshSession, user]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuthContext() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}

