"use client";

import type { ReactNode } from "react";
import Link from "next/link";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState } from "@/components/ui/ErrorState";
import { LoadingState } from "@/components/ui/LoadingState";
import { PageHeader } from "@/components/ui/PageHeader";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { useAuth } from "@/hooks/useAuth";
import { getAcademicYear, hardCloseAcademicYear, softCloseAcademicYear } from "@/lib/academic";
import type { Role } from "@/types/auth";

const rolloverRoles: Role[] = ["super_admin", "institute_owner", "accountant"];
const hardCloseRoles: Role[] = ["super_admin", "institute_owner"];

function DetailItem({ label, value }: { label: string; value?: ReactNode }) {
  return (
    <div>
      <dt className="text-xs font-semibold uppercase text-slate-500">{label}</dt>
      <dd className="mt-1 text-sm text-slate-800">{value || "Not set"}</dd>
    </div>
  );
}

export default function AcademicYearDetailPage({ params }: { params: { id: string } }) {
  const queryClient = useQueryClient();
  const { hasRole } = useAuth();
  const canSoftClose = rolloverRoles.some((role) => hasRole(role));
  const canHardClose = hardCloseRoles.some((role) => hasRole(role));
  const { data: year, error, isLoading } = useQuery({
    queryKey: ["academic-years", params.id],
    queryFn: () => getAcademicYear(params.id),
  });
  const refresh = () => void queryClient.invalidateQueries({ queryKey: ["academic-years", params.id] });
  const softClose = useMutation({ mutationFn: () => softCloseAcademicYear(params.id, { reason: "Closed from dashboard" }), onSuccess: refresh });
  const hardClose = useMutation({ mutationFn: () => hardCloseAcademicYear(params.id, { reason: "Hard closed from dashboard" }), onSuccess: refresh });

  return (
    <div className="space-y-5">
      <PageHeader
        actions={
          <div className="flex flex-wrap gap-2">
            {canSoftClose && year?.status !== "hard_closed" ? (
              <Button isLoading={softClose.isPending} onClick={() => softClose.mutate()} type="button" variant="secondary">
                Soft close
              </Button>
            ) : null}
            {canHardClose && year?.status !== "hard_closed" ? (
              <Button isLoading={hardClose.isPending} onClick={() => hardClose.mutate()} type="button">
                Hard close
              </Button>
            ) : null}
            <Link className="rounded-md border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50" href="/dashboard/academic-years">
              Back to academic years
            </Link>
          </div>
        }
        description="Year close actions are high-risk and validated by the backend."
        title={year?.name ?? "Academic year"}
      />
      {isLoading ? <LoadingState label="Loading academic year..." /> : null}
      {error ? <ErrorState message={error instanceof Error ? error.message : undefined} /> : null}
      {softClose.isSuccess ? <p className="rounded-md bg-green-50 px-4 py-3 text-sm font-medium text-green-700">Academic year soft closed.</p> : null}
      {hardClose.isSuccess ? <p className="rounded-md bg-green-50 px-4 py-3 text-sm font-medium text-green-700">Academic year hard closed.</p> : null}
      {softClose.isError || hardClose.isError ? <ErrorState title="Year close failed" /> : null}
      {year ? (
        <article className="rounded-lg bg-white p-5 shadow-[0_2px_18px_rgba(38,43,64,0.08)]">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h2 className="text-lg font-semibold text-[#262B40]">{year.name}</h2>
              <p className="mt-1 text-sm text-slate-500">Hard-closed years block future posting.</p>
            </div>
            <StatusBadge status={year.status} />
          </div>
          <dl className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <DetailItem label="AD start" value={year.ad_start_date} />
            <DetailItem label="AD end" value={year.ad_end_date} />
            <DetailItem label="BS start" value={year.bs_start_date} />
            <DetailItem label="BS end" value={year.bs_end_date} />
            <DetailItem label="Active" value={year.is_active ? "Yes" : "No"} />
            <DetailItem label="Notes" value={year.notes} />
          </dl>
          {year.status === "hard_closed" ? <p className="mt-5 rounded-md bg-red-50 px-3 py-2 text-sm font-medium text-red-700">This year is hard closed and read-only.</p> : null}
        </article>
      ) : null}
      {!isLoading && !error && !year ? <EmptyState title="Academic year not found" /> : null}
    </div>
  );
}
