"use client";

import type { ReactNode } from "react";
import Link from "next/link";
import { useRouteId } from "@/hooks/useRouteId";
import { useQuery } from "@tanstack/react-query";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState } from "@/components/ui/ErrorState";
import { LoadingState } from "@/components/ui/LoadingState";
import { MoneyDisplay } from "@/components/ui/MoneyDisplay";
import { PageHeader } from "@/components/ui/PageHeader";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { getTeacherPaymentBatch } from "@/lib/payroll";

function DetailItem({ label, value }: { label: string; value?: ReactNode }) {
  return (
    <div>
      <dt className="text-xs font-semibold uppercase text-slate-500">{label}</dt>
      <dd className="mt-1 text-sm text-slate-800">{value || "Not set"}</dd>
    </div>
  );
}

export default function TeacherPaymentBatchDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const id = useRouteId(params);
  const { data: batch, error, isLoading } = useQuery({
    enabled: Boolean(id),
    queryKey: ["teacher-payment-batches", id],
    queryFn: () => getTeacherPaymentBatch(id),
  });

  return (
    <div className="space-y-5">
      <PageHeader
        actions={
          <Link className="rounded-md border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50" href="/dashboard/payroll/payment-batches">
            Back to batches
          </Link>
        }
        description="Read-only teacher payment batch profile. Approval, posting, and payment generation are pending."
        title={batch?.batch_number ?? "Payment batch"}
      />

      {isLoading ? <LoadingState label="Loading payment batch..." /> : null}
      {error ? <ErrorState message={error instanceof Error ? error.message : undefined} /> : null}

      {batch ? (
        <section className="grid gap-4 lg:grid-cols-3">
          <article className="rounded-lg bg-white p-5 shadow-[0_2px_18px_rgba(38,43,64,0.08)] lg:col-span-2">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h2 className="text-lg font-semibold text-[#262B40]">{batch.batch_number}</h2>
                <p className="mt-1 text-sm text-slate-500">{batch.batch_date_ad}</p>
              </div>
              <StatusBadge status={batch.status} />
            </div>
            <dl className="mt-6 grid gap-4 sm:grid-cols-2">
              <DetailItem label="Total amount" value={<MoneyDisplay amount={batch.total_amount} />} />
              <DetailItem label="Academic year" value={batch.academic_year} />
              <DetailItem label="Academic period" value={batch.academic_period} />
              <DetailItem label="Approved at" value={batch.approved_at} />
              <DetailItem label="Posted at" value={batch.posted_at} />
            </dl>
          </article>
          <article className="rounded-lg bg-white p-5 shadow-[0_2px_18px_rgba(38,43,64,0.08)]">
            <h2 className="text-base font-semibold text-[#262B40]">Read-only Scope</h2>
            <p className="mt-4 text-sm leading-6 text-slate-700">
              Batch payment generation, approval, posting, and accounting entries are intentionally unavailable here.
            </p>
          </article>
          <article className="rounded-lg bg-white p-5 shadow-[0_2px_18px_rgba(38,43,64,0.08)] lg:col-span-3">
            <h2 className="text-base font-semibold text-[#262B40]">Description</h2>
            <p className="mt-4 text-sm leading-6 text-slate-700">{batch.description || batch.notes || "No description recorded."}</p>
          </article>
        </section>
      ) : null}

      {!isLoading && !error && !batch ? <EmptyState title="Payment batch not found" /> : null}
    </div>
  );
}
