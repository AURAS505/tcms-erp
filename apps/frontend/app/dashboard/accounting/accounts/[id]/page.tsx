"use client";

import Link from "next/link";
import { useRouteId } from "@/hooks/useRouteId";
import { useQuery } from "@tanstack/react-query";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState } from "@/components/ui/ErrorState";
import { LoadingState } from "@/components/ui/LoadingState";
import { PageHeader } from "@/components/ui/PageHeader";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { getAccount } from "@/lib/accounting";

function DetailItem({ label, value }: { label: string; value?: string | null }) {
  return (
    <div>
      <dt className="text-xs font-semibold uppercase text-slate-500">{label}</dt>
      <dd className="mt-1 text-sm text-slate-800">{value || "Not set"}</dd>
    </div>
  );
}

const formatLabel = (value?: string) =>
  value
    ? value
        .split("_")
        .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
        .join(" ")
    : "Not set";

export default function AccountDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const id = useRouteId(params);
  const { data: account, error, isLoading } = useQuery({
    enabled: Boolean(id),
    queryKey: ["accounts", id],
    queryFn: () => getAccount(id),
  });

  return (
    <div className="space-y-5">
      <PageHeader
        actions={
          <Link className="rounded-md border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50" href="/dashboard/accounting/accounts">
            Back to accounts
          </Link>
        }
        description="Read-only account profile. Account setup changes are not exposed here."
        title={account ? `${account.code} - ${account.name}` : "Account"}
      />

      {isLoading ? <LoadingState label="Loading account..." /> : null}
      {error ? <ErrorState message={error instanceof Error ? error.message : undefined} /> : null}

      {account ? (
        <section className="grid gap-4 lg:grid-cols-3">
          <article className="rounded-lg bg-white p-5 shadow-[0_2px_18px_rgba(38,43,64,0.08)] lg:col-span-2">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h2 className="text-lg font-semibold text-[#262B40]">{account.name}</h2>
                <p className="mt-1 text-sm text-slate-500">{account.code}</p>
              </div>
              <StatusBadge status={account.is_active ? "active" : "inactive"} />
            </div>
            <dl className="mt-6 grid gap-4 sm:grid-cols-2">
              <DetailItem label="Account type" value={formatLabel(account.account_type)} />
              <DetailItem label="Normal balance" value={formatLabel(account.normal_balance)} />
              <DetailItem label="Parent account" value={account.parent} />
              <DetailItem label="System account" value={account.is_system_account ? "Yes" : "No"} />
            </dl>
          </article>
          <article className="rounded-lg bg-white p-5 shadow-[0_2px_18px_rgba(38,43,64,0.08)]">
            <h2 className="text-base font-semibold text-[#262B40]">Description</h2>
            <p className="mt-4 text-sm leading-6 text-slate-700">{account.description || "No description recorded."}</p>
          </article>
        </section>
      ) : null}

      {!isLoading && !error && !account ? <EmptyState title="Account not found" /> : null}
    </div>
  );
}
