"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { Button } from "@/components/ui/Button";
import { useAuth } from "@/hooks/useAuth";
import type { User } from "@/types/auth";

interface TopbarProps {
  user: User | null;
}

export function Topbar({ user }: TopbarProps) {
  const router = useRouter();
  const { logout } = useAuth();
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  const handleLogout = async () => {
    setIsLoggingOut(true);
    try {
      await logout();
    } finally {
      router.push("/login");
      router.refresh();
    }
  };

  return (
    <header className="sticky top-0 z-10 border-b border-slate-200 bg-white">
      <div className="flex min-h-[60px] items-center justify-between gap-4 px-4 lg:px-7">
        <div>
          <p className="text-xs font-medium text-slate-500">Dashboard</p>
          <h2 className="text-base font-semibold text-[#262B40]">Overview</h2>
        </div>
        <div className="flex items-center gap-3">
          <div className="hidden text-right sm:block">
            <p className="text-sm font-semibold text-slate-800">{user?.fullName ?? "TCMS user"}</p>
            <p className="text-xs text-slate-500">{user?.roles?.[0]?.name ?? "Authenticated"}</p>
          </div>
          <Button isLoading={isLoggingOut} onClick={handleLogout} type="button" variant="secondary">
            Logout
          </Button>
        </div>
      </div>
    </header>
  );
}
