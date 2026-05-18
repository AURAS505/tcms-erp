"use client";

import { use } from "react";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { ErrorState } from "@/components/ui/ErrorState";
import { LoadingState } from "@/components/ui/LoadingState";
import { PageHeader } from "@/components/ui/PageHeader";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { getStudentInquiry } from "@/lib/students";

function DetailItem({ label, value }: { label: string; value?: string | null }) {
  return (
    <div>
      <dt className="text-xs font-semibold uppercase text-slate-500">{label}</dt>
      <dd className="mt-1 text-sm text-slate-800">{value || "Not set"}</dd>
    </div>
  );
}

export default function StudentInquiryDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const { data: inquiry, error, isLoading } = useQuery({
    queryKey: ["student-inquiries", id],
    queryFn: () => getStudentInquiry(id),
  });

  return (
    <div className="space-y-5">
      <PageHeader
        actions={
          <Link
            className="rounded-md border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50"
            href="/dashboard/student-inquiries"
          >
            Back to inquiries
          </Link>
        }
        description="Read-only inquiry detail. Conversion and admission approval workflows are pending."
        title={inquiry?.student_full_name ?? "Student inquiry"}
      />

      {isLoading ? <LoadingState label="Loading inquiry..." /> : null}
      {error ? <ErrorState message={error instanceof Error ? error.message : undefined} /> : null}

      {inquiry ? (
        <section className="grid gap-4 lg:grid-cols-3">
          <article className="rounded-lg bg-white p-5 shadow-[0_2px_18px_rgba(38,43,64,0.08)] lg:col-span-2">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h2 className="text-lg font-semibold text-[#262B40]">{inquiry.student_full_name}</h2>
                <p className="mt-1 text-sm text-slate-500">{inquiry.guardian_name}</p>
              </div>
              <StatusBadge status={inquiry.status} />
            </div>
            <dl className="mt-6 grid gap-4 sm:grid-cols-2">
              <DetailItem label="Contact number" value={inquiry.contact_number} />
              <DetailItem label="Email" value={inquiry.email} />
              <DetailItem label="Interested class or subject" value={inquiry.interested_class_subject} />
              <DetailItem label="Source" value={inquiry.inquiry_source} />
              <DetailItem label="Created" value={inquiry.created_at} />
              <DetailItem label="Updated" value={inquiry.updated_at} />
            </dl>
          </article>
          <article className="rounded-lg bg-white p-5 shadow-[0_2px_18px_rgba(38,43,64,0.08)]">
            <h2 className="text-base font-semibold text-[#262B40]">Notes</h2>
            <p className="mt-4 text-sm leading-6 text-slate-700">{inquiry.notes || "No notes recorded."}</p>
          </article>
        </section>
      ) : null}
    </div>
  );
}

