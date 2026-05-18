"use client";

import { use } from "react";
import type { ReactNode } from "react";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState } from "@/components/ui/ErrorState";
import { LoadingState } from "@/components/ui/LoadingState";
import { PageHeader } from "@/components/ui/PageHeader";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { getFeePlan } from "@/lib/billing";

function DetailItem({ label, value }: { label: string; value?: ReactNode }) {
  return (
    <div>
      <dt className="text-xs font-semibold uppercase text-slate-500">{label}</dt>
      <dd className="mt-1 text-sm text-slate-800">{value || "Not set"}</dd>
    </div>
  );
}

const formatLabel = (value?: string) =>
  value
    ? value
        .split("_")
        .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
        .join(" ")
    : "Not set";

export default function FeePlanDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const { data: plan, error, isLoading } = useQuery({
    queryKey: ["fee-plans", id],
    queryFn: () => getFeePlan(id),
  });

  return (
    <div className="space-y-5">
      <PageHeader
        actions={
          <Link className="rounded-md border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50" href="/dashboard/billing/fee-plans">
            Back to fee plans
          </Link>
        }
        description="Read-only fee plan profile. Plan item editing and approval workflows are pending."
        title={plan?.name ?? "Fee plan"}
      />

      {isLoading ? <LoadingState label="Loading fee plan..." /> : null}
      {error ? <ErrorState message={error instanceof Error ? error.message : undefined} /> : null}

      {plan ? (
        <section className="grid gap-4 lg:grid-cols-3">
          <article className="rounded-lg bg-white p-5 shadow-[0_2px_18px_rgba(38,43,64,0.08)] lg:col-span-2">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h2 className="text-lg font-semibold text-[#262B40]">{plan.name}</h2>
                <p className="mt-1 text-sm text-slate-500">{formatLabel(plan.fee_plan_type)}</p>
              </div>
              <StatusBadge status={plan.is_active ? "active" : "inactive"} />
            </div>
            <dl className="mt-6 grid gap-4 sm:grid-cols-2">
              <DetailItem label="Billing frequency" value={formatLabel(plan.billing_frequency)} />
              <DetailItem label="Payment due rule" value={formatLabel(plan.payment_due_rule)} />
              <DetailItem label="Due day" value={plan.due_day} />
              <DetailItem label="Class ID" value={plan.class_room} />
              <DetailItem label="Academic year" value={plan.academic_year} />
            </dl>
          </article>
          <article className="rounded-lg bg-white p-5 shadow-[0_2px_18px_rgba(38,43,64,0.08)]">
            <h2 className="text-base font-semibold text-[#262B40]">Read-only Scope</h2>
            <p className="mt-4 text-sm leading-6 text-slate-700">
              Fee plan item management is intentionally not exposed in this read-only billing foundation.
            </p>
          </article>
          <article className="rounded-lg bg-white p-5 shadow-[0_2px_18px_rgba(38,43,64,0.08)] lg:col-span-3">
            <h2 className="text-base font-semibold text-[#262B40]">Notes</h2>
            <p className="mt-4 text-sm leading-6 text-slate-700">{plan.notes || "No notes recorded."}</p>
          </article>
        </section>
      ) : null}

      {!isLoading && !error && !plan ? <EmptyState title="Fee plan not found" /> : null}
    </div>
  );
}
