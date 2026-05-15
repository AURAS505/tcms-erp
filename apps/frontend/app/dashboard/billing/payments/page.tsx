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
import { listStudentPayments } from "@/lib/billing";
import type { StudentPayment } from "@/types/billing";

const columns: SimpleTableColumn<StudentPayment>[] = [
  {
    header: "Receipt",
    render: (payment) => (
      <Link className="font-semibold text-[#0948B3] hover:underline" href={`/dashboard/billing/payments/${payment.id}`}>
        {payment.receipt_number || payment.draft_receipt_number || payment.id}
      </Link>
    ),
  },
  { header: "Student", render: (payment) => payment.student },
  { header: "Date", render: (payment) => payment.payment_date_ad },
  { header: "Method", render: (payment) => payment.payment_method },
  { header: "Net received", render: (payment) => <MoneyDisplay amount={payment.net_received_amount} /> },
  { header: "Status", render: (payment) => <StatusBadge status={payment.status} /> },
];

export default function PaymentsPage() {
  const [search, setSearch] = useState("");
  const { data, error, isLoading } = useQuery({
    queryKey: ["student-payments", search],
    queryFn: () => listStudentPayments(search),
  });

  return (
    <div className="space-y-5">
      <PageHeader
        actions={<SearchInput onChange={(event) => setSearch(event.target.value)} placeholder="Search payments" value={search} />}
        description="Read-only student payments. Approval, posting, void, and refund workflows are not exposed here."
        title="Payments"
      />

      {isLoading ? <LoadingState label="Loading payments..." /> : null}
      {error ? <ErrorState message={error instanceof Error ? error.message : undefined} /> : null}
      {data && data.data.length === 0 ? (
        <EmptyState message="No payments are available for your current branch context." title="No payments found" />
      ) : null}
      {data && data.data.length > 0 ? <SimpleTable columns={columns} getRowKey={(payment) => payment.id} rows={data.data} /> : null}
    </div>
  );
}
