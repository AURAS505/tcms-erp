"use client";

import { use } from "react";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState } from "@/components/ui/ErrorState";
import { LoadingState } from "@/components/ui/LoadingState";
import { PageHeader } from "@/components/ui/PageHeader";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { getClassEnrollment } from "@/lib/classes";

function DetailItem({ label, value }: { label: string; value?: string | null }) {
  return (
    <div>
      <dt className="text-xs font-semibold uppercase text-slate-500">{label}</dt>
      <dd className="mt-1 text-sm text-slate-800">{value || "Not set"}</dd>
    </div>
  );
}

export default function EnrollmentDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const { data: enrollment, error, isLoading } = useQuery({
    queryKey: ["class-enrollments", id],
    queryFn: () => getClassEnrollment(id),
  });

  return (
    <div className="space-y-5">
      <PageHeader
        actions={
          <Link className="rounded-md border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50" href="/dashboard/enrollments">
            Back to enrollments
          </Link>
        }
        description="Read-only enrollment profile. Creation, break, discount, and withdrawal workflows are pending."
        title="Enrollment profile"
      />

      {isLoading ? <LoadingState label="Loading enrollment..." /> : null}
      {error ? <ErrorState message={error instanceof Error ? error.message : undefined} /> : null}

      {enrollment ? (
        <section className="grid gap-4 lg:grid-cols-3">
          <article className="rounded-lg bg-white p-5 shadow-[0_2px_18px_rgba(38,43,64,0.08)] lg:col-span-2">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h2 className="text-lg font-semibold text-[#262B40]">{enrollment.id}</h2>
                <p className="mt-1 text-sm text-slate-500">
                  Student {enrollment.student} / Class {enrollment.class_room}
                </p>
              </div>
              <StatusBadge status={enrollment.status} />
            </div>
            <dl className="mt-6 grid gap-4 sm:grid-cols-2">
              <DetailItem label="Student ID" value={enrollment.student} />
              <DetailItem label="Class ID" value={enrollment.class_room} />
              <DetailItem label="Joined date" value={enrollment.joined_date_ad} />
              <DetailItem label="End date" value={enrollment.end_date_ad} />
              <DetailItem label="Left date" value={enrollment.left_date_ad} />
              <DetailItem label="Discount percent" value={enrollment.enrollment_discount_percentage} />
              <DetailItem label="Discount amount" value={enrollment.enrollment_discount_amount} />
              <DetailItem label="Teacher cut override" value={enrollment.teacher_cut_percentage_override} />
            </dl>
          </article>
          <article className="rounded-lg bg-white p-5 shadow-[0_2px_18px_rgba(38,43,64,0.08)]">
            <h2 className="text-base font-semibold text-[#262B40]">Related Workflow Records</h2>
            <p className="mt-4 text-sm leading-6 text-slate-700">
              Breaks, discounts, withdrawals, and teacher transfers are available through API helpers. Filtered enrollment sections are pending.
            </p>
          </article>
          <article className="rounded-lg bg-white p-5 shadow-[0_2px_18px_rgba(38,43,64,0.08)] lg:col-span-3">
            <h2 className="text-base font-semibold text-[#262B40]">Notes</h2>
            <p className="mt-4 text-sm leading-6 text-slate-700">{enrollment.notes || "No notes recorded."}</p>
          </article>
        </section>
      ) : null}

      {!isLoading && !error && !enrollment ? <EmptyState title="Enrollment not found" /> : null}
    </div>
  );
}
