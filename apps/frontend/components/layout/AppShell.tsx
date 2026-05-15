"use client";

import { useEffect, useState, type ReactNode } from "react";
import Link from "next/link";
import { Sidebar } from "@/components/layout/Sidebar";
import { Topbar } from "@/components/layout/Topbar";
import { authService } from "@/lib/auth";
import type { User } from "@/types/auth";

interface AppShellProps {
  children: ReactNode;
}

export function AppShell({ children }: AppShellProps) {
  const [user, setUser] = useState<User | null>(null);
  const [status, setStatus] = useState<"checking" | "authenticated" | "guest">("checking");

  useEffect(() => {
    let isMounted = true;

    authService
      .currentUser()
      .then((currentUser) => {
        if (!isMounted) return;
        setUser(currentUser);
        setStatus("authenticated");
      })
      .catch(() => {
        if (!isMounted) return;
        setUser(null);
        setStatus("guest");
      });

    return () => {
      isMounted = false;
    };
  }, []);

  if (status === "checking") {
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

  if (status === "guest") {
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
    <div className="min-h-screen bg-[#F5F8FB]">
      <Sidebar user={user} />
      <div className="lg:pl-64">
        <Topbar user={user} />
        <main className="px-4 py-6 lg:px-7">{children}</main>
      </div>
    </div>
  );
}
