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
import { listTeacherPayments } from "@/lib/payroll";
import type { TeacherPayment } from "@/types/payroll";

const columns: SimpleTableColumn<TeacherPayment>[] = [
  {
    header: "Voucher",
    render: (payment) => (
      <Link className="font-semibold text-[#0948B3] hover:underline" href={`/dashboard/payroll/payments/${payment.id}`}>
        {payment.voucher_number || payment.draft_voucher_number || payment.id}
      </Link>
    ),
  },
  { header: "Teacher", render: (payment) => payment.teacher },
  { header: "Date", render: (payment) => payment.payment_date_ad },
  { header: "Method", render: (payment) => payment.payment_method },
  { header: "Net paid", render: (payment) => <MoneyDisplay amount={payment.net_paid_amount} /> },
  { header: "Status", render: (payment) => <StatusBadge status={payment.status} /> },
];

export default function TeacherPaymentsPage() {
  const [search, setSearch] = useState("");
  const { data, error, isLoading } = useQuery({
    queryKey: ["teacher-payments", search],
    queryFn: () => listTeacherPayments(search),
  });

  return (
    <div className="space-y-5">
      <PageHeader
        actions={<SearchInput onChange={(event) => setSearch(event.target.value)} placeholder="Search teacher payments" value={search} />}
        description="Read-only teacher payments. Creation, approval, posting, voiding, and accounting actions are not exposed here."
        title="Teacher Payments"
      />

      {isLoading ? <LoadingState label="Loading teacher payments..." /> : null}
      {error ? <ErrorState message={error instanceof Error ? error.message : undefined} /> : null}
      {data && data.data.length === 0 ? (
        <EmptyState message="No teacher payments are available for your current branch context." title="No teacher payments found" />
      ) : null}
      {data && data.data.length > 0 ? <SimpleTable columns={columns} getRowKey={(payment) => payment.id} rows={data.data} /> : null}
    </div>
  );
}
