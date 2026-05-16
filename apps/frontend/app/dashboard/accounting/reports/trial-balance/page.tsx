"use client";

import { useSearchParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState } from "@/components/ui/ErrorState";
import { LoadingState } from "@/components/ui/LoadingState";
import { MoneyDisplay } from "@/components/ui/MoneyDisplay";
import { PageHeader } from "@/components/ui/PageHeader";
import { SimpleTable, type SimpleTableColumn } from "@/components/ui/SimpleTable";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { getTrialBalance } from "@/lib/accounting";
import type { AccountBalance, AccountingReportFilters } from "@/types/accounting";

function useReportFilters(): AccountingReportFilters {
  const searchParams = useSearchParams();
  return {
    organization: searchParams.get("organization"),
    branch: searchParams.get("branch"),
    academic_year: searchParams.get("academic_year"),
    academic_period: searchParams.get("academic_period"),
    date_from: searchParams.get("date_from"),
    date_to: searchParams.get("date_to"),
    include_zero_balances: searchParams.get("include_zero_balances") === "true",
  };
}

const columns: SimpleTableColumn<AccountBalance>[] = [
  { header: "Account", render: (line) => `${line.account_code} - ${line.account_name}` },
  { header: "Type", render: (line) => line.account_type.replaceAll("_", " ") },
  { header: "Debit", render: (line) => <MoneyDisplay amount={line.debit} /> },
  { header: "Credit", render: (line) => <MoneyDisplay amount={line.credit} /> },
];

export default function TrialBalancePage() {
  const filters = useReportFilters();
  const hasOrganization = Boolean(filters.organization);
  const { data, error, isLoading } = useQuery({
    queryKey: ["trial-balance", filters],
    queryFn: () => getTrialBalance(filters),
    enabled: hasOrganization,
  });

  return (
    <div className="space-y-5">
      <PageHeader
        description="Read-only trial balance. Add ?organization=<id> and optional date filters to load a report."
        title="Trial Balance"
      />

      {!hasOrganization ? <EmptyState message="Provide an organization query parameter to load this report." title="Report filters required" /> : null}
      {isLoading ? <LoadingState label="Loading trial balance..." /> : null}
      {error ? <ErrorState message={error instanceof Error ? error.message : undefined} /> : null}
      {data ? (
        <div className="space-y-4">
          <section className="grid gap-4 sm:grid-cols-3">
            <article className="rounded-lg bg-white p-4 shadow-[0_2px_18px_rgba(38,43,64,0.08)]">
              <p className="text-xs font-semibold uppercase text-slate-500">Total debit</p>
              <p className="mt-2 text-lg font-semibold text-[#262B40]"><MoneyDisplay amount={data.total_debit} /></p>
            </article>
            <article className="rounded-lg bg-white p-4 shadow-[0_2px_18px_rgba(38,43,64,0.08)]">
              <p className="text-xs font-semibold uppercase text-slate-500">Total credit</p>
              <p className="mt-2 text-lg font-semibold text-[#262B40]"><MoneyDisplay amount={data.total_credit} /></p>
            </article>
            <article className="rounded-lg bg-white p-4 shadow-[0_2px_18px_rgba(38,43,64,0.08)]">
              <p className="text-xs font-semibold uppercase text-slate-500">Balance status</p>
              <div className="mt-2"><StatusBadge status={data.is_balanced ? "balanced" : "out_of_balance"} /></div>
            </article>
          </section>
          {data.lines.length > 0 ? (
            <SimpleTable columns={columns} getRowKey={(line) => line.account_code} rows={data.lines} />
          ) : (
            <EmptyState message="No posted balances matched the selected filters." title="No trial balance lines" />
          )}
        </div>
      ) : null}
    </div>
  );
}
