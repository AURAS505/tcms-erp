"use client";

import { useSearchParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState } from "@/components/ui/ErrorState";
import { LoadingState } from "@/components/ui/LoadingState";
import { MoneyDisplay } from "@/components/ui/MoneyDisplay";
import { PageHeader } from "@/components/ui/PageHeader";
import { SimpleTable, type SimpleTableColumn } from "@/components/ui/SimpleTable";
import { getGeneralLedger } from "@/lib/accounting";
import type { AccountLedger, AccountingReportFilters } from "@/types/accounting";

function useReportFilters(): AccountingReportFilters {
  const searchParams = useSearchParams();
  return {
    organization: searchParams.get("organization"),
    branch: searchParams.get("branch"),
    academic_year: searchParams.get("academic_year"),
    academic_period: searchParams.get("academic_period"),
    account: searchParams.get("account"),
    date_from: searchParams.get("date_from"),
    date_to: searchParams.get("date_to"),
    include_zero_balances: searchParams.get("include_zero_balances") === "true",
  };
}

const columns: SimpleTableColumn<AccountLedger>[] = [
  { header: "Account", render: (ledger) => `${ledger.account_code} - ${ledger.account_name}` },
  { header: "Opening", render: (ledger) => <MoneyDisplay amount={ledger.opening_balance} /> },
  { header: "Debit", render: (ledger) => <MoneyDisplay amount={ledger.total_debit} /> },
  { header: "Credit", render: (ledger) => <MoneyDisplay amount={ledger.total_credit} /> },
  { header: "Closing", render: (ledger) => <MoneyDisplay amount={ledger.closing_balance} /> },
];

export default function GeneralLedgerPage() {
  const filters = useReportFilters();
  const hasOrganization = Boolean(filters.organization);
  const { data, error, isLoading } = useQuery({
    queryKey: ["general-ledger", filters],
    queryFn: () => getGeneralLedger(filters),
    enabled: hasOrganization,
  });

  return (
    <div className="space-y-5">
      <PageHeader
        description="Read-only general ledger. Add ?organization=<id> and optional account/date filters to load a report."
        title="General Ledger"
      />

      {!hasOrganization ? <EmptyState message="Provide an organization query parameter to load this report." title="Report filters required" /> : null}
      {isLoading ? <LoadingState label="Loading general ledger..." /> : null}
      {error ? <ErrorState message={error instanceof Error ? error.message : undefined} /> : null}
      {data && data.length === 0 ? <EmptyState message="No ledger balances matched the selected filters." title="No ledger data" /> : null}
      {data && data.length > 0 ? <SimpleTable columns={columns} getRowKey={(ledger) => ledger.account_code} rows={data} /> : null}
    </div>
  );
}
