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
import { listFeePlans } from "@/lib/billing";
import type { FeePlan } from "@/types/billing";

const formatLabel = (value: string) =>
  value
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");

const columns: SimpleTableColumn<FeePlan>[] = [
  {
    header: "Plan",
    render: (plan) => (
      <Link className="font-semibold text-[#0948B3] hover:underline" href={`/dashboard/billing/fee-plans/${plan.id}`}>
        {plan.name}
      </Link>
    ),
  },
  { header: "Type", render: (plan) => formatLabel(plan.fee_plan_type) },
  { header: "Frequency", render: (plan) => formatLabel(plan.billing_frequency) },
  { header: "Due rule", render: (plan) => formatLabel(plan.payment_due_rule) },
  { header: "Status", render: (plan) => <StatusBadge status={plan.is_active ? "active" : "inactive"} /> },
];

export default function FeePlansPage() {
  const [search, setSearch] = useState("");
  const { data, error, isLoading } = useQuery({
    queryKey: ["fee-plans", search],
    queryFn: () => listFeePlans(search),
  });

  return (
    <div className="space-y-5">
      <PageHeader
        actions={<SearchInput onChange={(event) => setSearch(event.target.value)} placeholder="Search fee plans" value={search} />}
        description="Read-only fee plan records. Create and approval workflows are not exposed here."
        title="Fee Plans"
      />

      {isLoading ? <LoadingState label="Loading fee plans..." /> : null}
      {error ? <ErrorState message={error instanceof Error ? error.message : undefined} /> : null}
      {data && data.data.length === 0 ? (
        <EmptyState message="No fee plans are available for your current branch context." title="No fee plans found" />
      ) : null}
      {data && data.data.length > 0 ? <SimpleTable columns={columns} getRowKey={(plan) => plan.id} rows={data.data} /> : null}
    </div>
  );
}
