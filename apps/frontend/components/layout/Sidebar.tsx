"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { getNavigationForRoles } from "@/config/navigation";
import type { User } from "@/types/auth";

interface SidebarProps {
  user: User | null;
}

export function Sidebar({ user }: SidebarProps) {
  const pathname = usePathname();
  const items = getNavigationForRoles(user?.roles.map((role) => role.code) ?? []);

  return (
    <aside className="fixed inset-y-0 left-0 z-20 hidden w-64 bg-[#262B40] text-slate-200 lg:block">
      <div className="flex h-full flex-col">
        <div className="border-b border-white/10 px-5 py-5">
          <div className="text-lg font-bold text-white">TCMS ERP</div>
          <p className="mt-1 text-xs text-slate-400">Education operations</p>
        </div>

        <div className="border-b border-white/10 px-5 py-4">
          <div className="text-sm font-semibold text-white">{user?.fullName ?? "Session pending"}</div>
          <div className="mt-1 truncate text-xs text-slate-400">{user?.email ?? "Checking access"}</div>
        </div>

        <nav className="flex-1 space-y-1 px-3 py-4">
          <p className="px-3 pb-2 text-[11px] font-semibold uppercase text-slate-400">Core</p>
          {items.map((item) => {
            const isActive = pathname === item.href || (item.href !== "/dashboard" && pathname.startsWith(`${item.href}/`));
            return (
              <Link
                className={`block rounded-md px-3 py-2 text-sm font-medium transition ${
                  isActive ? "bg-[#0948B3] text-white" : "text-slate-300 hover:bg-white/10 hover:text-white"
                }`}
                href={item.href}
                key={item.href}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>

        <div className="border-t border-white/10 px-5 py-4 text-xs leading-5 text-slate-400">
          Branch permissions are enforced by the backend.
        </div>
      </div>
    </aside>
  );
}
