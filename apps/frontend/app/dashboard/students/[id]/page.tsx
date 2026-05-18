"use client";

import Link from "next/link";
import { useRouteId } from "@/hooks/useRouteId";
import { useQuery } from "@tanstack/react-query";
import { ErrorState } from "@/components/ui/ErrorState";
import { LoadingState } from "@/components/ui/LoadingState";
import { DetailCard } from "@/components/ui/DetailCard";
import { DetailGrid, DetailItem } from "@/components/ui/DetailGrid";
import { PageHeader } from "@/components/ui/PageHeader";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { getStudent } from "@/lib/students";

export default function StudentDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const id = useRouteId(params);
  const { data: student, error, isLoading } = useQuery({
    enabled: Boolean(id),
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
          <DetailCard
            actions={<StatusBadge status={student.status} />}
            className="lg:col-span-2"
            description={student.admission_number}
            title={student.full_name}
          >
            <DetailGrid>
              <DetailItem label="Preferred name" value={student.preferred_name} />
              <DetailItem label="Gender" value={student.gender} />
              <DetailItem label="Phone" value={student.phone} />
              <DetailItem label="Email" value={student.email} />
              <DetailItem label="Current class" value={student.current_grade_class} />
              <DetailItem label="School or college" value={student.school_college_name} />
              <DetailItem label="Admission date AD" value={student.admission_date_ad} />
              <DetailItem label="Admission date BS" value={student.admission_date_bs} />
            </DetailGrid>
          </DetailCard>
          <DetailCard title="Address and notes">
            <div className="space-y-3">
              <DetailItem label="Permanent address" value={student.permanent_address} />
              <DetailItem label="Temporary address" value={student.temporary_address} />
              <DetailItem label="Notes" value={student.notes} />
            </div>
          </DetailCard>
          <DetailCard className="lg:col-span-3" title="Guardian relationships">
            <p className="mt-2 text-sm leading-6 text-slate-600">
              Guardian and family links will appear here after the student-guardian endpoint supports direct student filtering.
            </p>
          </DetailCard>
        </section>
      ) : null}
    </div>
  );
}
