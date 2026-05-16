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
import { getTeacherPayment } from "@/lib/payroll";

function DetailItem({ label, value }: { label: string; value?: ReactNode }) {
  return (
    <div>
      <dt className="text-xs font-semibold uppercase text-slate-500">{label}</dt>
      <dd className="mt-1 text-sm text-slate-800">{value || "Not set"}</dd>
    </div>
  );
}

export default function TeacherPaymentDetailPage({ params }: { params: { id: string } }) {
  const { data: payment, error, isLoading } = useQuery({
    queryKey: ["teacher-payments", params.id],
    queryFn: () => getTeacherPayment(params.id),
  });

  return (
    <div className="space-y-5">
      <PageHeader
        actions={
          <Link className="rounded-md border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50" href="/dashboard/payroll/payments">
            Back to teacher payments
          </Link>
        }
        description="Read-only teacher payment profile. Creation, approval, posting, and void workflows are pending."
        title={payment?.voucher_number || payment?.draft_voucher_number || "Teacher payment"}
      />

      {isLoading ? <LoadingState label="Loading teacher payment..." /> : null}
      {error ? <ErrorState message={error instanceof Error ? error.message : undefined} /> : null}

      {payment ? (
        <section className="grid gap-4 lg:grid-cols-3">
          <article className="rounded-lg bg-white p-5 shadow-[0_2px_18px_rgba(38,43,64,0.08)] lg:col-span-2">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h2 className="text-lg font-semibold text-[#262B40]">{payment.voucher_number || payment.draft_voucher_number || payment.id}</h2>
                <p className="mt-1 text-sm text-slate-500">Teacher {payment.teacher}</p>
              </div>
              <StatusBadge status={payment.status} />
            </div>
            <dl className="mt-6 grid gap-4 sm:grid-cols-2">
              <DetailItem label="Payment date" value={payment.payment_date_ad} />
              <DetailItem label="Method" value={payment.payment_method} />
              <DetailItem label="Amount" value={<MoneyDisplay amount={payment.amount} />} />
              <DetailItem label="Deduction" value={<MoneyDisplay amount={payment.deduction_amount} />} />
              <DetailItem label="Net paid" value={<MoneyDisplay amount={payment.net_paid_amount} />} />
              <DetailItem label="Reference" value={payment.reference_number} />
              <DetailItem label="Batch ID" value={payment.payment_batch} />
              <DetailItem label="Posted at" value={payment.posted_at} />
            </dl>
          </article>
          <article className="rounded-lg bg-white p-5 shadow-[0_2px_18px_rgba(38,43,64,0.08)]">
            <h2 className="text-base font-semibold text-[#262B40]">Accounting Boundary</h2>
            <p className="mt-4 text-sm leading-6 text-slate-700">
              Payment approval, posting, voiding, allocation edits, and accounting entries are intentionally not available here.
            </p>
          </article>
          <article className="rounded-lg bg-white p-5 shadow-[0_2px_18px_rgba(38,43,64,0.08)] lg:col-span-3">
            <h2 className="text-base font-semibold text-[#262B40]">Notes</h2>
            <p className="mt-4 text-sm leading-6 text-slate-700">{payment.notes || payment.void_reason || "No notes recorded."}</p>
          </article>
        </section>
      ) : null}

      {!isLoading && !error && !payment ? <EmptyState title="Teacher payment not found" /> : null}
    </div>
  );
}
