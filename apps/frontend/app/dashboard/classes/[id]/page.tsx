"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState } from "@/components/ui/ErrorState";
import { LoadingState } from "@/components/ui/LoadingState";
import { PageHeader } from "@/components/ui/PageHeader";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { getClass } from "@/lib/classes";

function DetailItem({ label, value }: { label: string; value?: string | number | null }) {
  return (
    <div>
      <dt className="text-xs font-semibold uppercase text-slate-500">{label}</dt>
      <dd className="mt-1 text-sm text-slate-800">{value ?? "Not set"}</dd>
    </div>
  );
}

export default function ClassDetailPage({ params }: { params: { id: string } }) {
  const { data: classRoom, error, isLoading } = useQuery({
    queryKey: ["classes", params.id],
    queryFn: () => getClass(params.id),
  });

  return (
    <div className="space-y-5">
      <PageHeader
        actions={
          <Link className="rounded-md border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50" href="/dashboard/classes">
            Back to classes
          </Link>
        }
        description="Read-only class profile. Create, edit, scheduling, and enrollment workflows are pending."
        title={classRoom?.class_name ?? "Class profile"}
      />

      {isLoading ? <LoadingState label="Loading class..." /> : null}
      {error ? <ErrorState message={error instanceof Error ? error.message : undefined} /> : null}

      {classRoom ? (
        <section className="grid gap-4 lg:grid-cols-3">
          <article className="rounded-lg bg-white p-5 shadow-[0_2px_18px_rgba(38,43,64,0.08)] lg:col-span-2">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h2 className="text-lg font-semibold text-[#262B40]">{classRoom.class_name}</h2>
                <p className="mt-1 text-sm text-slate-500">
                  {[classRoom.batch_name, classRoom.section_name].filter(Boolean).join(" / ") || "No batch or section set"}
                </p>
              </div>
              <StatusBadge status={classRoom.status} />
            </div>
            <dl className="mt-6 grid gap-4 sm:grid-cols-2">
              <DetailItem label="Capacity" value={classRoom.capacity} />
              <DetailItem label="Monthly fee" value={classRoom.monthly_fee} />
              <DetailItem label="Start date" value={classRoom.start_date_ad} />
              <DetailItem label="Expected end date" value={classRoom.expected_end_date_ad} />
              <DetailItem label="Payment due rule" value={classRoom.payment_due_rule} />
              <DetailItem label="Due day" value={classRoom.due_day} />
              <DetailItem label="Teacher payment type" value={classRoom.teacher_payment_type} />
              <DetailItem label="Teacher cut" value={classRoom.teacher_cut_percentage} />
            </dl>
          </article>
          <article className="rounded-lg bg-white p-5 shadow-[0_2px_18px_rgba(38,43,64,0.08)]">
            <h2 className="text-base font-semibold text-[#262B40]">Schedules and Enrollments</h2>
            <p className="mt-4 text-sm leading-6 text-slate-700">
              Related schedules and enrollments will appear here after direct class filtering is available in the frontend.
            </p>
          </article>
          <article className="rounded-lg bg-white p-5 shadow-[0_2px_18px_rgba(38,43,64,0.08)] lg:col-span-3">
            <h2 className="text-base font-semibold text-[#262B40]">Notes</h2>
            <p className="mt-4 text-sm leading-6 text-slate-700">{classRoom.notes || "No notes recorded."}</p>
          </article>
        </section>
      ) : null}

      {!isLoading && !error && !classRoom ? <EmptyState title="Class not found" /> : null}
    </div>
  );
}
