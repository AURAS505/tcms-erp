"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { getNavigationGroupsForRoles } from "@/config/navigation";
import type { User } from "@/types/auth";

interface SidebarProps {
  className?: string;
  onNavigate?: () => void;
  user: User | null;
}

function getInitials(user: User | null) {
  const source = user?.fullName ?? user?.username ?? "TCMS";
  const initials = source
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0])
    .join("");

  return initials.toUpperCase() || "TC";
}

export function Sidebar({ className, onNavigate, user }: SidebarProps) {
  const pathname = usePathname();
  const groups = getNavigationGroupsForRoles(user?.roles.map((role) => role.code) ?? []);
  const primaryRole = user?.roles?.[0]?.name ?? "Authenticated";

  return (
    <aside
      aria-label="Primary navigation"
      className={
        className ??
        "fixed inset-y-0 left-0 z-20 hidden w-64 flex-col border-r border-white/10 bg-[#262B40] text-slate-200 shadow-[12px_0_28px_rgba(15,23,42,0.16)] lg:flex"
      }
    >
      <div className="flex h-full flex-col">
        <div className="border-b border-white/10 px-5 py-5">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-white text-sm font-bold text-[#262B40] shadow-sm">
              TC
            </div>
            <div>
              <div className="text-base font-bold tracking-wide text-white">TCMS ERP</div>
              <p className="mt-0.5 text-xs font-medium text-slate-400">Education operations</p>
            </div>
          </div>
        </div>

        <div className="border-b border-white/10 px-5 py-4">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-[#0948B3] text-xs font-bold text-white">
              {getInitials(user)}
            </div>
            <div className="min-w-0">
              <div className="truncate text-sm font-semibold text-white">{user?.fullName ?? "Session pending"}</div>
              <div className="mt-0.5 truncate text-xs text-slate-400">{primaryRole}</div>
            </div>
          </div>
          <div className="mt-3 truncate rounded-md bg-white/5 px-2.5 py-1.5 text-xs text-slate-400">
            {user?.email ?? "Checking access"}
          </div>
        </div>

        <nav className="flex-1 overflow-y-auto px-3 py-4">
          {groups.length === 0 ? (
            <p className="rounded-md border border-white/10 bg-white/5 px-3 py-3 text-sm text-slate-400">
              No navigation is available for this role.
            </p>
          ) : (
            <div className="space-y-5">
              {groups.map((group) => (
                <section aria-label={group.description} key={group.label}>
                  <p className="px-3 pb-2 text-[11px] font-bold uppercase tracking-[0.14em] text-slate-500">
                    {group.label}
                  </p>
                  <div className="space-y-1">
                    {group.items.map((item) => {
                      const isActive =
                        pathname === item.href || (item.href !== "/dashboard" && pathname.startsWith(`${item.href}/`));
                      return (
                        <Link
                          aria-current={isActive ? "page" : undefined}
                          className={`group relative block rounded-lg px-3 py-2 text-sm font-semibold transition ${
                            isActive
                              ? "bg-white text-[#262B40] shadow-sm"
                              : "text-slate-300 hover:bg-white/10 hover:text-white"
                          }`}
                          href={item.href}
                          key={item.href}
                          onClick={onNavigate}
                        >
                          {isActive ? (
                            <span className="absolute inset-y-2 left-0 w-1 rounded-r-full bg-[#0948B3]" />
                          ) : null}
                          <span className="pl-1">{item.label}</span>
                        </Link>
                      );
                    })}
                  </div>
                </section>
              ))}
            </div>
          )}
        </nav>

        <div className="border-t border-white/10 px-5 py-4">
          <div className="rounded-lg bg-white/5 px-3 py-2.5 text-xs leading-5 text-slate-400">
            Branch access and financial permissions are enforced by the backend.
          </div>
        </div>
      </div>
    </aside>
  );
}
