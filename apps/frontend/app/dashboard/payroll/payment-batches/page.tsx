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
import { listTeacherPaymentBatches } from "@/lib/payroll";
import type { TeacherPaymentBatch } from "@/types/payroll";

const columns: SimpleTableColumn<TeacherPaymentBatch>[] = [
  {
    header: "Batch",
    render: (batch) => (
      <Link className="font-semibold text-[#0948B3] hover:underline" href={`/dashboard/payroll/payment-batches/${batch.id}`}>
        {batch.batch_number}
      </Link>
    ),
  },
  { header: "Date", render: (batch) => batch.batch_date_ad },
  { header: "Total", render: (batch) => <MoneyDisplay amount={batch.total_amount} /> },
  { header: "Status", render: (batch) => <StatusBadge status={batch.status} /> },
];

export default function TeacherPaymentBatchesPage() {
  const [search, setSearch] = useState("");
  const { data, error, isLoading } = useQuery({
    queryKey: ["teacher-payment-batches", search],
    queryFn: () => listTeacherPaymentBatches(search),
  });

  return (
    <div className="space-y-5">
      <PageHeader
        actions={<SearchInput onChange={(event) => setSearch(event.target.value)} placeholder="Search payment batches" value={search} />}
        description="Read-only teacher payment batches. Approval and posting actions are not exposed here."
        title="Payment Batches"
      />

      {isLoading ? <LoadingState label="Loading payment batches..." /> : null}
      {error ? <ErrorState message={error instanceof Error ? error.message : undefined} /> : null}
      {data && data.data.length === 0 ? (
        <EmptyState message="No teacher payment batches are available for your current branch context." title="No payment batches found" />
      ) : null}
      {data && data.data.length > 0 ? <SimpleTable columns={columns} getRowKey={(batch) => batch.id} rows={data.data} /> : null}
    </div>
  );
}
