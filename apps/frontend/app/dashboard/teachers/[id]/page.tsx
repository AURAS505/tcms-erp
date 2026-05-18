"use client";

import { use } from "react";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState } from "@/components/ui/ErrorState";
import { LoadingState } from "@/components/ui/LoadingState";
import { PageHeader } from "@/components/ui/PageHeader";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { getTeacher } from "@/lib/teachers";

function DetailItem({ label, value }: { label: string; value?: string | null }) {
  return (
    <div>
      <dt className="text-xs font-semibold uppercase text-slate-500">{label}</dt>
      <dd className="mt-1 text-sm text-slate-800">{value || "Not set"}</dd>
    </div>
  );
}

export default function TeacherDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const { data: teacher, error, isLoading } = useQuery({
    queryKey: ["teachers", id],
    queryFn: () => getTeacher(id),
  });

  return (
    <div className="space-y-5">
      <PageHeader
        actions={
          <Link className="rounded-md border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50" href="/dashboard/teachers">
            Back to teachers
          </Link>
        }
        description="Read-only teacher profile. Create, edit, and contract workflows are pending."
        title={teacher?.full_name ?? "Teacher profile"}
      />

      {isLoading ? <LoadingState label="Loading teacher..." /> : null}
      {error ? <ErrorState message={error instanceof Error ? error.message : undefined} /> : null}

      {teacher ? (
        <section className="grid gap-4 lg:grid-cols-3">
          <article className="rounded-lg bg-white p-5 shadow-[0_2px_18px_rgba(38,43,64,0.08)] lg:col-span-2">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h2 className="text-lg font-semibold text-[#262B40]">{teacher.full_name}</h2>
                <p className="mt-1 text-sm text-slate-500">{teacher.employee_number}</p>
              </div>
              <StatusBadge status={teacher.status} />
            </div>
            <dl className="mt-6 grid gap-4 sm:grid-cols-2">
              <DetailItem label="Preferred name" value={teacher.preferred_name} />
              <DetailItem label="Gender" value={teacher.gender} />
              <DetailItem label="Phone" value={teacher.phone} />
              <DetailItem label="Alternate phone" value={teacher.alternate_phone} />
              <DetailItem label="Email" value={teacher.email} />
              <DetailItem label="Joining date" value={teacher.joining_date_ad} />
              <DetailItem label="Qualification" value={teacher.qualification} />
              <DetailItem label="Specialization" value={teacher.specialization} />
            </dl>
          </article>
          <article className="rounded-lg bg-white p-5 shadow-[0_2px_18px_rgba(38,43,64,0.08)]">
            <h2 className="text-base font-semibold text-[#262B40]">Contracts and Activity</h2>
            <p className="mt-4 text-sm leading-6 text-slate-700">
              Contracts, activities, and status history are available through API helpers. Filtered teacher sections are pending.
            </p>
          </article>
          <article className="rounded-lg bg-white p-5 shadow-[0_2px_18px_rgba(38,43,64,0.08)] lg:col-span-2">
            <h2 className="text-base font-semibold text-[#262B40]">Experience</h2>
            <p className="mt-4 text-sm leading-6 text-slate-700">{teacher.experience_summary || "No experience summary recorded."}</p>
          </article>
          <article className="rounded-lg bg-white p-5 shadow-[0_2px_18px_rgba(38,43,64,0.08)]">
            <h2 className="text-base font-semibold text-[#262B40]">Address</h2>
            <p className="mt-4 text-sm leading-6 text-slate-700">{teacher.address || "No address recorded."}</p>
          </article>
        </section>
      ) : null}

      {!isLoading && !error && !teacher ? <EmptyState title="Teacher not found" /> : null}
    </div>
  );
}
