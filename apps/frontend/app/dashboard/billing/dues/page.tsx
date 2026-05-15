"use client";

import Link from "next/link";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState } from "@/components/ui/ErrorState";
import { LoadingState } from "@/components/ui/LoadingState";
import { MoneyDisplay } from "@/components/ui/MoneyDisplay";
import { PageHeader } from "@/components/ui/PageHeader";
import { SearchInput } from "@/components/ui/SearchInput";
import { SimpleTable, type SimpleTableColumn } from "@/components/ui/SimpleTable";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { listFeeDues } from "@/lib/billing";
import type { StudentFeeDue } from "@/types/billing";

const columns: SimpleTableColumn<StudentFeeDue>[] = [
  {
    header: "Period",
    render: (due) => (
      <Link className="font-semibold text-[#0948B3] hover:underline" href={`/dashboard/billing/dues/${due.id}`}>
        {due.period_label}
      </Link>
    ),
  },
  { header: "Student", render: (due) => due.student },
  { header: "Due date", render: (due) => due.due_date_ad || "Not set" },
  { header: "Net", render: (due) => <MoneyDisplay amount={due.net_amount} /> },
  { header: "Balance", render: (due) => <MoneyDisplay amount={due.balance_amount} /> },
  { header: "Status", render: (due) => <StatusBadge status={due.status} /> },
];

export default function FeeDuesPage() {
  const [search, setSearch] = useState("");
  const { data, error, isLoading } = useQuery({
    queryKey: ["fee-dues", search],
    queryFn: () => listFeeDues(search),
  });

  return (
    <div className="space-y-5">
      <PageHeader
        actions={<SearchInput onChange={(event) => setSearch(event.target.value)} placeholder="Search dues" value={search} />}
        description="Read-only student fee dues. Approval, write-off, and payment workflows are not exposed here."
        title="Fee Dues"
      />

      {isLoading ? <LoadingState label="Loading fee dues..." /> : null}
      {error ? <ErrorState message={error instanceof Error ? error.message : undefined} /> : null}
      {data && data.data.length === 0 ? (
        <EmptyState message="No fee dues are available for your current branch context." title="No fee dues found" />
      ) : null}
      {data && data.data.length > 0 ? <SimpleTable columns={columns} getRowKey={(due) => due.id} rows={data.data} /> : null}
    </div>
  );
}
