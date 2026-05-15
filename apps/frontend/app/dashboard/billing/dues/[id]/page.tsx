"use client";

import type { ReactNode } from "react";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState } from "@/components/ui/ErrorState";
import { LoadingState } from "@/components/ui/LoadingState";
import { MoneyDisplay } from "@/components/ui/MoneyDisplay";
import { PageHeader } from "@/components/ui/PageHeader";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { getFeeDue } from "@/lib/billing";

function DetailItem({ label, value }: { label: string; value?: ReactNode }) {
  return (
    <div>
      <dt className="text-xs font-semibold uppercase text-slate-500">{label}</dt>
      <dd className="mt-1 text-sm text-slate-800">{value || "Not set"}</dd>
    </div>
  );
}

export default function FeeDueDetailPage({ params }: { params: { id: string } }) {
  const { data: due, error, isLoading } = useQuery({
    queryKey: ["fee-dues", params.id],
    queryFn: () => getFeeDue(params.id),
  });

  return (
    <div className="space-y-5">
      <PageHeader
        actions={
          <Link className="rounded-md border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50" href="/dashboard/billing/dues">
            Back to dues
          </Link>
        }
        description="Read-only fee due profile. Approval, write-off, and payment workflows are pending."
        title={due?.period_label ?? "Fee due"}
      />

      {isLoading ? <LoadingState label="Loading fee due..." /> : null}
      {error ? <ErrorState message={error instanceof Error ? error.message : undefined} /> : null}

      {due ? (
        <section className="grid gap-4 lg:grid-cols-3">
          <article className="rounded-lg bg-white p-5 shadow-[0_2px_18px_rgba(38,43,64,0.08)] lg:col-span-2">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h2 className="text-lg font-semibold text-[#262B40]">{due.period_label}</h2>
                <p className="mt-1 text-sm text-slate-500">Student {due.student}</p>
              </div>
              <StatusBadge status={due.status} />
            </div>
            <dl className="mt-6 grid gap-4 sm:grid-cols-2">
              <DetailItem label="Due date" value={due.due_date_ad} />
              <DetailItem label="Original amount" value={<MoneyDisplay amount={due.original_amount} />} />
              <DetailItem label="Discount" value={<MoneyDisplay amount={due.discount_amount} />} />
              <DetailItem label="Fine" value={<MoneyDisplay amount={due.fine_amount} />} />
              <DetailItem label="Net amount" value={<MoneyDisplay amount={due.net_amount} />} />
              <DetailItem label="Paid amount" value={<MoneyDisplay amount={due.paid_amount} />} />
              <DetailItem label="Balance" value={<MoneyDisplay amount={due.balance_amount} />} />
              <DetailItem label="Fee plan ID" value={due.fee_plan} />
            </dl>
          </article>
          <article className="rounded-lg bg-white p-5 shadow-[0_2px_18px_rgba(38,43,64,0.08)]">
            <h2 className="text-base font-semibold text-[#262B40]">Accounting Boundary</h2>
            <p className="mt-4 text-sm leading-6 text-slate-700">
              This view does not approve, write off, collect, or post fee dues.
            </p>
          </article>
          <article className="rounded-lg bg-white p-5 shadow-[0_2px_18px_rgba(38,43,64,0.08)] lg:col-span-3">
            <h2 className="text-base font-semibold text-[#262B40]">Notes</h2>
            <p className="mt-4 text-sm leading-6 text-slate-700">{due.notes || due.cancellation_reason || "No notes recorded."}</p>
          </article>
        </section>
      ) : null}

      {!isLoading && !error && !due ? <EmptyState title="Fee due not found" /> : null}
    </div>
  );
}
