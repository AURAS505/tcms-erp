"use client";

import type { ReactNode } from "react";
import { useEffect, useState } from "react";
import Link from "next/link";
import { Sidebar } from "@/components/layout/Sidebar";
import { Topbar } from "@/components/layout/Topbar";
import { useAuth } from "@/hooks/useAuth";

interface AppShellProps {
  children: ReactNode;
}

export function AppShell({ children }: AppShellProps) {
  const { isAuthenticated, isLoading, user } = useAuth();
  const [isMobileNavigationOpen, setIsMobileNavigationOpen] = useState(false);

  useEffect(() => {
    if (!isMobileNavigationOpen) return undefined;

    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        setIsMobileNavigationOpen(false);
      }
    }

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [isMobileNavigationOpen]);

  if (isLoading) {
    return (
      <div
        aria-live="polite"
        className="min-h-screen bg-[#F5F8FB] p-8 text-sm text-slate-600"
        role="status"
      >
        Checking session...
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-[#F5F8FB] px-4">
        <section className="max-w-md rounded-lg bg-white p-7 text-center shadow-[0_2px_18px_rgba(38,43,64,0.08)]">
          <h1 className="text-xl font-semibold text-[#262B40]">Authentication required</h1>
          <p className="mt-2 text-sm leading-6 text-slate-500">
            The dashboard shell is protected. Sign in to load your role and branch context.
          </p>
          <Link
            className="mt-5 inline-flex rounded-md bg-[#0948B3] px-4 py-2 text-sm font-semibold text-white hover:bg-[#073a91]"
            href="/login"
          >
            Go to login
          </Link>
        </section>
      </main>
    );
  }

  return (
    <div className="min-h-screen bg-[var(--tcms-color-bg)]">
      <Sidebar user={user} />
      {isMobileNavigationOpen ? (
        <div
          className="fixed inset-0 z-40 lg:hidden"
          role="dialog"
          aria-label="Mobile navigation"
          aria-modal="true"
          id="mobile-primary-navigation"
        >
          <button
            aria-label="Close navigation"
            className="absolute inset-0 bg-slate-950/50"
            onClick={() => setIsMobileNavigationOpen(false)}
            type="button"
          />
          <Sidebar
            className="relative z-50 flex h-full w-72 max-w-[86vw] flex-col border-r border-white/10 bg-[#262B40] text-slate-200 shadow-2xl"
            onNavigate={() => setIsMobileNavigationOpen(false)}
            user={user}
          />
        </div>
      ) : null}
      <div className="lg:pl-64">
        <Topbar
          isMenuOpen={isMobileNavigationOpen}
          onMenuClick={() => setIsMobileNavigationOpen(true)}
          user={user}
        />
        <main className="mx-auto w-full max-w-[1600px] px-4 py-6 sm:px-5 lg:px-7">{children}</main>
      </div>
    </div>
  );
}
