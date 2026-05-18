"use client";

import { usePathname, useRouter } from "next/navigation";
import { useState } from "react";
import { Button } from "@/components/ui/Button";
import { useAuth } from "@/hooks/useAuth";
import type { User } from "@/types/auth";

interface TopbarProps {
  onMenuClick?: () => void;
  user: User | null;
}

function formatSegment(segment: string) {
  return decodeURIComponent(segment)
    .replaceAll("-", " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

export function Topbar({ onMenuClick, user }: TopbarProps) {
  const pathname = usePathname();
  const router = useRouter();
  const { logout } = useAuth();
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const segments = pathname.split("/").filter(Boolean).filter((segment) => segment !== "dashboard");
  const lastSegment = segments[segments.length - 1];
  const title = lastSegment ? formatSegment(lastSegment) : "Overview";
  const primaryRole = user?.roles?.[0]?.name ?? "Authenticated";

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
    <header className="sticky top-0 z-10 border-b border-[var(--tcms-color-border)] bg-white/95 backdrop-blur">
      <div className="flex min-h-[66px] items-center justify-between gap-4 px-4 sm:px-5 lg:px-7">
        <div className="flex min-w-0 items-center gap-3">
          <button
            aria-label="Open navigation"
            className="inline-flex h-10 w-10 flex-col items-center justify-center gap-1 rounded-lg border border-[var(--tcms-color-border)] bg-white text-[#262B40] shadow-sm transition hover:bg-slate-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--tcms-color-focus)] focus-visible:ring-offset-2 lg:hidden"
            onClick={onMenuClick}
            type="button"
          >
            <span aria-hidden="true" className="h-0.5 w-4 rounded-full bg-current" />
            <span aria-hidden="true" className="h-0.5 w-4 rounded-full bg-current" />
            <span aria-hidden="true" className="h-0.5 w-4 rounded-full bg-current" />
          </button>
          <div className="min-w-0">
            <div className="flex items-center gap-2 text-xs font-semibold text-slate-500">
              <span>Dashboard</span>
              {segments.length > 0 ? (
                <>
                  <span aria-hidden="true">/</span>
                  <span className="truncate">{formatSegment(segments[0])}</span>
                </>
              ) : null}
            </div>
            <h2 className="truncate text-lg font-bold text-[#262B40]">{title}</h2>
          </div>
        </div>
        <div className="flex shrink-0 items-center gap-3">
          <div className="hidden rounded-full border border-[#DDE7F3] bg-[#F5F8FB] px-3 py-1 text-xs font-semibold text-slate-600 md:block">
            ERP Console
          </div>
          <div className="hidden text-right sm:block">
            <p className="text-sm font-semibold text-slate-800">{user?.fullName ?? "TCMS user"}</p>
            <p className="text-xs text-slate-500">{primaryRole}</p>
          </div>
          <Button isLoading={isLoggingOut} onClick={handleLogout} type="button" variant="secondary">
            Logout
          </Button>
        </div>
      </div>
    </header>
  );
}
