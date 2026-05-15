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
import { getStudentPayment } from "@/lib/billing";

function DetailItem({ label, value }: { label: string; value?: ReactNode }) {
  return (
    <div>
      <dt className="text-xs font-semibold uppercase text-slate-500">{label}</dt>
      <dd className="mt-1 text-sm text-slate-800">{value || "Not set"}</dd>
    </div>
  );
}

export default function PaymentDetailPage({ params }: { params: { id: string } }) {
  const { data: payment, error, isLoading } = useQuery({
    queryKey: ["student-payments", params.id],
    queryFn: () => getStudentPayment(params.id),
  });

  return (
    <div className="space-y-5">
      <PageHeader
        actions={
          <Link className="rounded-md border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50" href="/dashboard/billing/payments">
            Back to payments
          </Link>
        }
        description="Read-only payment profile. Approval, posting, void, and refund workflows are pending."
        title={payment?.receipt_number || payment?.draft_receipt_number || "Payment"}
      />

      {isLoading ? <LoadingState label="Loading payment..." /> : null}
      {error ? <ErrorState message={error instanceof Error ? error.message : undefined} /> : null}

      {payment ? (
        <section className="grid gap-4 lg:grid-cols-3">
          <article className="rounded-lg bg-white p-5 shadow-[0_2px_18px_rgba(38,43,64,0.08)] lg:col-span-2">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h2 className="text-lg font-semibold text-[#262B40]">{payment.receipt_number || payment.draft_receipt_number || payment.id}</h2>
                <p className="mt-1 text-sm text-slate-500">Student {payment.student}</p>
              </div>
              <StatusBadge status={payment.status} />
            </div>
            <dl className="mt-6 grid gap-4 sm:grid-cols-2">
              <DetailItem label="Payment date" value={payment.payment_date_ad} />
              <DetailItem label="Method" value={payment.payment_method} />
              <DetailItem label="Amount" value={<MoneyDisplay amount={payment.amount} />} />
              <DetailItem label="Discount" value={<MoneyDisplay amount={payment.discount_amount} />} />
              <DetailItem label="Fine" value={<MoneyDisplay amount={payment.fine_amount} />} />
              <DetailItem label="Net received" value={<MoneyDisplay amount={payment.net_received_amount} />} />
              <DetailItem label="Reference" value={payment.reference_number} />
              <DetailItem label="Advance payment" value={payment.is_advance_payment ? "Yes" : "No"} />
            </dl>
          </article>
          <article className="rounded-lg bg-white p-5 shadow-[0_2px_18px_rgba(38,43,64,0.08)]">
            <h2 className="text-base font-semibold text-[#262B40]">Accounting Boundary</h2>
            <p className="mt-4 text-sm leading-6 text-slate-700">
              Payment approval, posting, voiding, refunding, and accounting entries are intentionally not available here.
            </p>
          </article>
          <article className="rounded-lg bg-white p-5 shadow-[0_2px_18px_rgba(38,43,64,0.08)] lg:col-span-3">
            <h2 className="text-base font-semibold text-[#262B40]">Notes</h2>
            <p className="mt-4 text-sm leading-6 text-slate-700">{payment.notes || payment.void_reason || "No notes recorded."}</p>
          </article>
        </section>
      ) : null}

      {!isLoading && !error && !payment ? <EmptyState title="Payment not found" /> : null}
    </div>
  );
}
