"use client";

import Link from "next/link";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState } from "@/components/ui/ErrorState";
import { LoadingState } from "@/components/ui/LoadingState";
import { PageHeader } from "@/components/ui/PageHeader";
import { SearchInput } from "@/components/ui/SearchInput";
import { SimpleTable, type SimpleTableColumn } from "@/components/ui/SimpleTable";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { listAccounts } from "@/lib/accounting";
import type { Account } from "@/types/accounting";

const formatLabel = (value: string) =>
  value
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");

const columns: SimpleTableColumn<Account>[] = [
  {
    header: "Code",
    render: (account) => (
      <Link className="font-semibold text-[#0948B3] hover:underline" href={`/dashboard/accounting/accounts/${account.id}`}>
        {account.code}
      </Link>
    ),
  },
  { header: "Account", render: (account) => account.name },
  { header: "Type", render: (account) => formatLabel(account.account_type) },
  { header: "Normal", render: (account) => formatLabel(account.normal_balance) },
  { header: "Status", render: (account) => <StatusBadge status={account.is_active ? "active" : "inactive"} /> },
];

export default function AccountsPage() {
  const [search, setSearch] = useState("");
  const { data, error, isLoading } = useQuery({
    queryKey: ["accounts", search],
    queryFn: () => listAccounts(search),
  });

  return (
    <div className="space-y-5">
      <PageHeader
        actions={<SearchInput onChange={(event) => setSearch(event.target.value)} placeholder="Search accounts" value={search} />}
        description="Read-only chart of accounts. Account creation and configuration workflows are not exposed here."
        title="Chart of Accounts"
      />

      {isLoading ? <LoadingState label="Loading accounts..." /> : null}
      {error ? <ErrorState message={error instanceof Error ? error.message : undefined} /> : null}
      {data && data.data.length === 0 ? <EmptyState message="No accounts are available." title="No accounts found" /> : null}
      {data && data.data.length > 0 ? <SimpleTable columns={columns} getRowKey={(account) => account.id} rows={data.data} /> : null}
    </div>
  );
}
