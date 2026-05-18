"use client";

import { use } from "react";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState } from "@/components/ui/ErrorState";
import { LoadingState } from "@/components/ui/LoadingState";
import { PageHeader } from "@/components/ui/PageHeader";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { getTeacherContract } from "@/lib/teachers";

function DetailItem({ label, value }: { label: string; value?: string | null }) {
  return (
    <div>
      <dt className="text-xs font-semibold uppercase text-slate-500">{label}</dt>
      <dd className="mt-1 text-sm text-slate-800">{value || "Not set"}</dd>
    </div>
  );
}

const formatContractType = (value?: string) =>
  value
    ? value
        .split("_")
        .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
        .join(" ")
    : "Not set";

export default function TeacherContractDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const { data: contract, error, isLoading } = useQuery({
    queryKey: ["teacher-contracts", id],
    queryFn: () => getTeacherContract(id),
  });

  return (
    <div className="space-y-5">
      <PageHeader
        actions={
          <Link className="rounded-md border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50" href="/dashboard/teacher-contracts">
            Back to contracts
          </Link>
        }
        description="Read-only teacher contract profile. Create, edit, payroll, and payment workflows are pending."
        title="Teacher contract"
      />

      {isLoading ? <LoadingState label="Loading teacher contract..." /> : null}
      {error ? <ErrorState message={error instanceof Error ? error.message : undefined} /> : null}

      {contract ? (
        <section className="grid gap-4 lg:grid-cols-3">
          <article className="rounded-lg bg-white p-5 shadow-[0_2px_18px_rgba(38,43,64,0.08)] lg:col-span-2">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h2 className="text-lg font-semibold text-[#262B40]">{formatContractType(contract.contract_type)}</h2>
                <p className="mt-1 text-sm text-slate-500">Teacher {contract.teacher}</p>
              </div>
              <StatusBadge status={contract.is_active ? "active" : "inactive"} />
            </div>
            <dl className="mt-6 grid gap-4 sm:grid-cols-2">
              <DetailItem label="Teacher ID" value={contract.teacher} />
              <DetailItem label="Academic year" value={contract.academic_year} />
              <DetailItem label="Effective from" value={contract.effective_from_ad} />
              <DetailItem label="Effective to" value={contract.effective_to_ad} />
              <DetailItem label="Teacher cut percent" value={contract.default_teacher_cut_percentage} />
              <DetailItem label="Package amount" value={contract.package_amount} />
              <DetailItem label="Fixed monthly salary" value={contract.fixed_monthly_salary} />
            </dl>
          </article>
          <article className="rounded-lg bg-white p-5 shadow-[0_2px_18px_rgba(38,43,64,0.08)]">
            <h2 className="text-base font-semibold text-[#262B40]">Payroll Boundary</h2>
            <p className="mt-4 text-sm leading-6 text-slate-700">
              This page only displays contract data. Payroll earning and payment workflows are intentionally separate.
            </p>
          </article>
          <article className="rounded-lg bg-white p-5 shadow-[0_2px_18px_rgba(38,43,64,0.08)] lg:col-span-3">
            <h2 className="text-base font-semibold text-[#262B40]">Notes</h2>
            <p className="mt-4 text-sm leading-6 text-slate-700">{contract.notes || "No notes recorded."}</p>
          </article>
        </section>
      ) : null}

      {!isLoading && !error && !contract ? <EmptyState title="Teacher contract not found" /> : null}
    </div>
  );
}
