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
import { getTeacherEarning } from "@/lib/payroll";

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

export default function TeacherEarningDetailPage({ params }: { params: { id: string } }) {
  const { data: earning, error, isLoading } = useQuery({
    queryKey: ["teacher-earnings", params.id],
    queryFn: () => getTeacherEarning(params.id),
  });

  return (
    <div className="space-y-5">
      <PageHeader
        actions={
          <Link className="rounded-md border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50" href="/dashboard/payroll/earnings">
            Back to earnings
          </Link>
        }
        description="Read-only teacher earning profile. Approval, posting, and payment processing are pending."
        title={earning?.period_label || "Teacher earning"}
      />

      {isLoading ? <LoadingState label="Loading teacher earning..." /> : null}
      {error ? <ErrorState message={error instanceof Error ? error.message : undefined} /> : null}

      {earning ? (
        <section className="grid gap-4 lg:grid-cols-3">
          <article className="rounded-lg bg-white p-5 shadow-[0_2px_18px_rgba(38,43,64,0.08)] lg:col-span-2">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h2 className="text-lg font-semibold text-[#262B40]">{earning.period_label || earning.id}</h2>
                <p className="mt-1 text-sm text-slate-500">Teacher {earning.teacher}</p>
              </div>
              <StatusBadge status={earning.status} />
            </div>
            <dl className="mt-6 grid gap-4 sm:grid-cols-2">
              <DetailItem label="Source" value={formatLabel(earning.earning_source)} />
              <DetailItem label="Earning date" value={earning.earning_date_ad} />
              <DetailItem label="Gross" value={<MoneyDisplay amount={earning.gross_amount} />} />
              <DetailItem label="Deduction" value={<MoneyDisplay amount={earning.deduction_amount} />} />
              <DetailItem label="Net" value={<MoneyDisplay amount={earning.net_amount} />} />
              <DetailItem label="Paid" value={<MoneyDisplay amount={earning.paid_amount} />} />
              <DetailItem label="Balance" value={<MoneyDisplay amount={earning.balance_amount} />} />
              <DetailItem label="Student payment ID" value={earning.student_payment} />
            </dl>
          </article>
          <article className="rounded-lg bg-white p-5 shadow-[0_2px_18px_rgba(38,43,64,0.08)]">
            <h2 className="text-base font-semibold text-[#262B40]">Accounting Boundary</h2>
            <p className="mt-4 text-sm leading-6 text-slate-700">
              This view does not approve, post, reverse, pay, or create accounting entries for earnings.
            </p>
          </article>
          <article className="rounded-lg bg-white p-5 shadow-[0_2px_18px_rgba(38,43,64,0.08)] lg:col-span-3">
            <h2 className="text-base font-semibold text-[#262B40]">Notes</h2>
            <p className="mt-4 text-sm leading-6 text-slate-700">{earning.notes || "No notes recorded."}</p>
          </article>
        </section>
      ) : null}

      {!isLoading && !error && !earning ? <EmptyState title="Teacher earning not found" /> : null}
    </div>
  );
}
