"use client";

import { use } from "react";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { ErrorState } from "@/components/ui/ErrorState";
import { LoadingState } from "@/components/ui/LoadingState";
import { PageHeader } from "@/components/ui/PageHeader";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { getStudent } from "@/lib/students";

function DetailItem({ label, value }: { label: string; value?: string | null }) {
  return (
    <div>
      <dt className="text-xs font-semibold uppercase text-slate-500">{label}</dt>
      <dd className="mt-1 text-sm text-slate-800">{value || "Not set"}</dd>
    </div>
  );
}

export default function StudentDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const { data: student, error, isLoading } = useQuery({
    queryKey: ["students", id],
    queryFn: () => getStudent(id),
  });

  return (
    <div className="space-y-5">
      <PageHeader
        actions={
          <Link className="rounded-md border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50" href="/dashboard/students">
            Back to students
          </Link>
        }
        description="Read-only admission profile. Create, edit, and approval workflows are pending."
        title={student?.full_name ?? "Student profile"}
      />

      {isLoading ? <LoadingState label="Loading student..." /> : null}
      {error ? <ErrorState message={error instanceof Error ? error.message : undefined} /> : null}

      {student ? (
        <section className="grid gap-4 lg:grid-cols-3">
          <article className="rounded-lg bg-white p-5 shadow-[0_2px_18px_rgba(38,43,64,0.08)] lg:col-span-2">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h2 className="text-lg font-semibold text-[#262B40]">{student.full_name}</h2>
                <p className="mt-1 text-sm text-slate-500">{student.admission_number}</p>
              </div>
              <StatusBadge status={student.status} />
            </div>
            <dl className="mt-6 grid gap-4 sm:grid-cols-2">
              <DetailItem label="Preferred name" value={student.preferred_name} />
              <DetailItem label="Gender" value={student.gender} />
              <DetailItem label="Phone" value={student.phone} />
              <DetailItem label="Email" value={student.email} />
              <DetailItem label="Current class" value={student.current_grade_class} />
              <DetailItem label="School or college" value={student.school_college_name} />
              <DetailItem label="Admission date AD" value={student.admission_date_ad} />
              <DetailItem label="Admission date BS" value={student.admission_date_bs} />
            </dl>
          </article>
          <article className="rounded-lg bg-white p-5 shadow-[0_2px_18px_rgba(38,43,64,0.08)]">
            <h2 className="text-base font-semibold text-[#262B40]">Address and notes</h2>
            <dl className="mt-4 space-y-4">
              <DetailItem label="Permanent address" value={student.permanent_address} />
              <DetailItem label="Temporary address" value={student.temporary_address} />
              <DetailItem label="Notes" value={student.notes} />
            </dl>
          </article>
          <article className="rounded-lg bg-white p-5 shadow-[0_2px_18px_rgba(38,43,64,0.08)] lg:col-span-3">
            <h2 className="text-base font-semibold text-[#262B40]">Guardian relationships</h2>
            <p className="mt-2 text-sm leading-6 text-slate-600">
              Guardian and family links will appear here after the student-guardian endpoint supports direct student filtering.
            </p>
          </article>
        </section>
      ) : null}
    </div>
  );
}
