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
import { getInvoice } from "@/lib/billing";

function DetailItem({ label, value }: { label: string; value?: ReactNode }) {
  return (
    <div>
      <dt className="text-xs font-semibold uppercase text-slate-500">{label}</dt>
      <dd className="mt-1 text-sm text-slate-800">{value || "Not set"}</dd>
    </div>
  );
}

export default function InvoiceDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const id = useRouteId(params);
  const { data: invoice, error, isLoading } = useQuery({
    enabled: Boolean(id),
    queryKey: ["invoices", id],
    queryFn: () => getInvoice(id),
  });

  return (
    <div className="space-y-5">
      <PageHeader
        actions={
          <Link className="rounded-md border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50" href="/dashboard/billing/invoices">
            Back to invoices
          </Link>
        }
        description="Read-only invoice profile. Posting, voiding, and collection workflows are pending."
        title={invoice?.invoice_number ?? "Invoice"}
      />

      {isLoading ? <LoadingState label="Loading invoice..." /> : null}
      {error ? <ErrorState message={error instanceof Error ? error.message : undefined} /> : null}

      {invoice ? (
        <section className="grid gap-4 lg:grid-cols-3">
          <article className="rounded-lg bg-white p-5 shadow-[0_2px_18px_rgba(38,43,64,0.08)] lg:col-span-2">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h2 className="text-lg font-semibold text-[#262B40]">{invoice.invoice_number}</h2>
                <p className="mt-1 text-sm text-slate-500">Student {invoice.student}</p>
              </div>
              <StatusBadge status={invoice.status} />
            </div>
            <dl className="mt-6 grid gap-4 sm:grid-cols-2">
              <DetailItem label="Invoice date" value={invoice.invoice_date_ad} />
              <DetailItem label="Due date" value={invoice.due_date_ad} />
              <DetailItem label="Subtotal" value={<MoneyDisplay amount={invoice.subtotal} />} />
              <DetailItem label="Discount" value={<MoneyDisplay amount={invoice.discount_amount} />} />
              <DetailItem label="Fine" value={<MoneyDisplay amount={invoice.fine_amount} />} />
              <DetailItem label="Total" value={<MoneyDisplay amount={invoice.total_amount} />} />
              <DetailItem label="Paid" value={<MoneyDisplay amount={invoice.paid_amount} />} />
              <DetailItem label="Balance" value={<MoneyDisplay amount={invoice.balance_amount} />} />
            </dl>
          </article>
          <article className="rounded-lg bg-white p-5 shadow-[0_2px_18px_rgba(38,43,64,0.08)]">
            <h2 className="text-base font-semibold text-[#262B40]">Read-only Scope</h2>
            <p className="mt-4 text-sm leading-6 text-slate-700">
              Invoice item details and payment allocation sections will be added after filtered relationship views are available.
            </p>
          </article>
          <article className="rounded-lg bg-white p-5 shadow-[0_2px_18px_rgba(38,43,64,0.08)] lg:col-span-3">
            <h2 className="text-base font-semibold text-[#262B40]">Notes</h2>
            <p className="mt-4 text-sm leading-6 text-slate-700">{invoice.notes || "No notes recorded."}</p>
          </article>
        </section>
      ) : null}

      {!isLoading && !error && !invoice ? <EmptyState title="Invoice not found" /> : null}
    </div>
  );
}
