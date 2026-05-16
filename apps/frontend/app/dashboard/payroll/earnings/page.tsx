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
import { listTeacherEarnings } from "@/lib/payroll";
import type { TeacherEarning } from "@/types/payroll";

const formatLabel = (value: string) =>
  value
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");

const columns: SimpleTableColumn<TeacherEarning>[] = [
  {
    header: "Earning",
    render: (earning) => (
      <Link className="font-semibold text-[#0948B3] hover:underline" href={`/dashboard/payroll/earnings/${earning.id}`}>
        {earning.period_label || earning.id}
      </Link>
    ),
  },
  { header: "Teacher", render: (earning) => earning.teacher },
  { header: "Source", render: (earning) => formatLabel(earning.earning_source) },
  { header: "Date", render: (earning) => earning.earning_date_ad },
  { header: "Net", render: (earning) => <MoneyDisplay amount={earning.net_amount} /> },
  { header: "Status", render: (earning) => <StatusBadge status={earning.status} /> },
];

export default function TeacherEarningsPage() {
  const [search, setSearch] = useState("");
  const { data, error, isLoading } = useQuery({
    queryKey: ["teacher-earnings", search],
    queryFn: () => listTeacherEarnings(search),
  });

  return (
    <div className="space-y-5">
      <PageHeader
        actions={<SearchInput onChange={(event) => setSearch(event.target.value)} placeholder="Search teacher earnings" value={search} />}
        description="Read-only teacher earnings. Approval, posting, and payment processing are not exposed here."
        title="Teacher Earnings"
      />

      {isLoading ? <LoadingState label="Loading teacher earnings..." /> : null}
      {error ? <ErrorState message={error instanceof Error ? error.message : undefined} /> : null}
      {data && data.data.length === 0 ? (
        <EmptyState message="No teacher earnings are available for your current branch context." title="No teacher earnings found" />
      ) : null}
      {data && data.data.length > 0 ? <SimpleTable columns={columns} getRowKey={(earning) => earning.id} rows={data.data} /> : null}
    </div>
  );
}
