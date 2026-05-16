"use client";

import { useSearchParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState } from "@/components/ui/ErrorState";
import { LoadingState } from "@/components/ui/LoadingState";
import { MoneyDisplay } from "@/components/ui/MoneyDisplay";
import { PageHeader } from "@/components/ui/PageHeader";
import { getProfitLoss } from "@/lib/accounting";
import type { AccountingReportFilters, ProfitLossReport } from "@/types/accounting";

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

export default function ProfitLossPage() {
  const filters = useReportFilters();
  const hasOrganization = Boolean(filters.organization);
  const { data, error, isLoading } = useQuery<ProfitLossReport>({
    queryKey: ["profit-loss", filters],
    queryFn: () => getProfitLoss(filters),
    enabled: hasOrganization,
  });

  return (
    <div className="space-y-5">
      <PageHeader
        description="Read-only profit and loss summary. Add ?organization=<id> and optional date filters to load a report."
        title="Profit & Loss"
      />

      {!hasOrganization ? <EmptyState message="Provide an organization query parameter to load this report." title="Report filters required" /> : null}
      {isLoading ? <LoadingState label="Loading profit and loss..." /> : null}
      {error ? <ErrorState message={error instanceof Error ? error.message : undefined} /> : null}
      {data ? (
        <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <SummaryCard label="Revenue" value={data.total_revenue} />
          <SummaryCard label="Contra revenue" value={data.total_contra_revenue} />
          <SummaryCard label="Expenses" value={data.total_expenses} />
          <SummaryCard label="Other income" value={data.total_other_income} />
          <SummaryCard label="Other expenses" value={data.total_other_expenses} />
          <SummaryCard label="Net profit/loss" value={data.net_profit_loss} />
        </section>
      ) : null}
    </div>
  );
}
