"use client";

import type { ReactNode } from "react";
import Link from "next/link";
import { useRouteId } from "@/hooks/useRouteId";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState } from "@/components/ui/ErrorState";
import { LoadingState } from "@/components/ui/LoadingState";
import { MoneyDisplay } from "@/components/ui/MoneyDisplay";
import { PageHeader } from "@/components/ui/PageHeader";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { useAuth } from "@/hooks/useAuth";
import { approveTeacherEarning, getTeacherEarning, postTeacherEarning } from "@/lib/payroll";
import type { Role } from "@/types/auth";

const financialRoles: Role[] = ["super_admin", "institute_owner", "accountant"];
const immutableStatuses = ["posted", "partial", "paid", "cancelled", "reversed"];

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

export default function TeacherEarningDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const id = useRouteId(params);
  const queryClient = useQueryClient();
  const { hasRole } = useAuth();
  const canMutate = financialRoles.some((role) => hasRole(role));
  const { data: earning, error, isLoading, refetch } = useQuery({
    enabled: Boolean(id),
    queryKey: ["teacher-earnings", id],
    queryFn: () => getTeacherEarning(id),
  });
  const approveMutation = useMutation({
    mutationFn: () => approveTeacherEarning(id),
    onSuccess: async (updatedEarning) => {
      queryClient.setQueryData(["teacher-earnings", id], updatedEarning);
      await queryClient.invalidateQueries({ queryKey: ["teacher-earnings"] });
      await refetch();
    },
  });
  const postMutation = useMutation({
    mutationFn: () => postTeacherEarning(id),
    onSuccess: async (updatedEarning) => {
      queryClient.setQueryData(["teacher-earnings", id], updatedEarning);
      await queryClient.invalidateQueries({ queryKey: ["teacher-earnings"] });
      await refetch();
    },
  });

  const canApprove = Boolean(earning && canMutate && ["draft", "pending_approval"].includes(earning.status));
  const canPost = Boolean(earning && canMutate && earning.status === "approved");
  const isImmutable = Boolean(earning && immutableStatuses.includes(earning.status));

  return (
    <div className="space-y-5">
      <PageHeader
        actions={
          <>
            {canApprove ? (
              <Button isLoading={approveMutation.isPending} onClick={() => approveMutation.mutate()} type="button">
                Approve earning
              </Button>
            ) : null}
            {canPost ? (
              <Button isLoading={postMutation.isPending} onClick={() => postMutation.mutate()} type="button">
                Post earning
              </Button>
            ) : null}
            <Link className="rounded-md border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50" href="/dashboard/payroll/earnings">
              Back to earnings
            </Link>
          </>
        }
        description="Teacher earning profile. Approval and posting use secured backend payroll workflow APIs."
        title={earning?.period_label || "Teacher earning"}
      />

      {isLoading ? <LoadingState label="Loading teacher earning..." /> : null}
      {error ? <ErrorState message={error instanceof Error ? error.message : undefined} /> : null}
      {approveMutation.isError ? (
        <ErrorState
          message={approveMutation.error instanceof Error ? approveMutation.error.message : "Unable to approve teacher earning."}
          title="Approval failed"
        />
      ) : null}
      {postMutation.isError ? (
        <ErrorState
          message={postMutation.error instanceof Error ? postMutation.error.message : "Unable to post teacher earning."}
          title="Posting failed"
        />
      ) : null}
      {approveMutation.isSuccess ? (
        <div className="rounded-lg border border-green-100 bg-green-50 p-4 text-sm font-medium text-green-700">
          Teacher earning approved.
        </div>
      ) : null}
      {postMutation.isSuccess ? (
        <div className="rounded-lg border border-green-100 bg-green-50 p-4 text-sm font-medium text-green-700">
          Teacher earning posted.
        </div>
      ) : null}
      {isImmutable ? (
        <div className="rounded-lg border border-slate-200 bg-white p-4 text-sm text-slate-600">
          This teacher earning is {earning?.status} and is read-only. Changes and accounting entries must use dedicated backend workflows.
        </div>
      ) : null}

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
              The frontend does not calculate ledger effects. Posting sends this earning to the backend workflow, which validates state and posts accounting entries.
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
