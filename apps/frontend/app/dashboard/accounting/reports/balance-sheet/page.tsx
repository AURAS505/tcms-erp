"use client";

import { useSearchParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState } from "@/components/ui/ErrorState";
import { LoadingState } from "@/components/ui/LoadingState";
import { MoneyDisplay } from "@/components/ui/MoneyDisplay";
import { PageHeader } from "@/components/ui/PageHeader";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { getBalanceSheet } from "@/lib/accounting";
import type { AccountingReportFilters, BalanceSheetReport } from "@/types/accounting";

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

function SummaryCard({ label, value }: { label: string; value: string }) {
  return (
    <article className="rounded-lg bg-white p-4 shadow-[0_2px_18px_rgba(38,43,64,0.08)]">
      <p className="text-xs font-semibold uppercase text-slate-500">{label}</p>
      <p className="mt-2 text-lg font-semibold text-[#262B40]"><MoneyDisplay amount={value} /></p>
    </article>
  );
}

export default function BalanceSheetPage() {
  const filters = useReportFilters();
  const hasOrganization = Boolean(filters.organization);
  const { data, error, isLoading } = useQuery<BalanceSheetReport>({
    queryKey: ["balance-sheet", filters],
    queryFn: () => getBalanceSheet(filters),
    enabled: hasOrganization,
  });

  return (
    <div className="space-y-5">
      <PageHeader
        description="Read-only balance sheet summary. Add ?organization=<id> and optional date filters to load a report."
        title="Balance Sheet"
      />

      {!hasOrganization ? <EmptyState message="Provide an organization query parameter to load this report." title="Report filters required" /> : null}
      {isLoading ? <LoadingState label="Loading balance sheet..." /> : null}
      {error ? <ErrorState message={error instanceof Error ? error.message : undefined} /> : null}
      {data ? (
        <div className="space-y-4">
          <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <SummaryCard label="Assets" value={data.total_assets} />
            <SummaryCard label="Liabilities" value={data.total_liabilities} />
            <SummaryCard label="Equity" value={data.total_equity} />
            <SummaryCard label="Liabilities + equity" value={data.total_liabilities_and_equity} />
          </section>
          <article className="rounded-lg bg-white p-4 shadow-[0_2px_18px_rgba(38,43,64,0.08)]">
            <p className="text-xs font-semibold uppercase text-slate-500">Balance status</p>
            <div className="mt-2"><StatusBadge status={data.is_balanced ? "balanced" : "out_of_balance"} /></div>
          </article>
        </div>
      ) : null}
    </div>
  );
}
