"use client";

import { use } from "react";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState } from "@/components/ui/ErrorState";
import { LoadingState } from "@/components/ui/LoadingState";
import { PageHeader } from "@/components/ui/PageHeader";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { getSubject } from "@/lib/classes";

function DetailItem({ label, value }: { label: string; value?: string | null }) {
  return (
    <div>
      <dt className="text-xs font-semibold uppercase text-slate-500">{label}</dt>
      <dd className="mt-1 text-sm text-slate-800">{value || "Not set"}</dd>
    </div>
  );
}

export default function SubjectDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const { data: subject, error, isLoading } = useQuery({
    queryKey: ["subjects", id],
    queryFn: () => getSubject(id),
  });

  return (
    <div className="space-y-5">
      <PageHeader
        actions={
          <Link className="rounded-md border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50" href="/dashboard/subjects">
            Back to subjects
          </Link>
        }
        description="Read-only subject record. Create and edit workflows are pending."
        title={subject?.subject_name ?? "Subject profile"}
      />

      {isLoading ? <LoadingState label="Loading subject..." /> : null}
      {error ? <ErrorState message={error instanceof Error ? error.message : undefined} /> : null}

      {subject ? (
        <article className="rounded-lg bg-white p-5 shadow-[0_2px_18px_rgba(38,43,64,0.08)]">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h2 className="text-lg font-semibold text-[#262B40]">{subject.subject_name}</h2>
              <p className="mt-1 text-sm text-slate-500">{subject.subject_code}</p>
            </div>
            <StatusBadge status={subject.is_active ? "active" : "inactive"} />
          </div>
          <dl className="mt-6 grid gap-4 sm:grid-cols-2">
            <DetailItem label="Subject code" value={subject.subject_code} />
            <DetailItem label="Created" value={subject.created_at} />
            <DetailItem label="Updated" value={subject.updated_at} />
          </dl>
          <p className="mt-6 text-sm leading-6 text-slate-700">{subject.description || "No description recorded."}</p>
        </article>
      ) : null}

      {!isLoading && !error && !subject ? <EmptyState title="Subject not found" /> : null}
    </div>
  );
}
