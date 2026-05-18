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
import { approveTeacherPayment, getTeacherPayment, postTeacherPayment } from "@/lib/payroll";
import type { Role } from "@/types/auth";

const financialRoles: Role[] = ["super_admin", "institute_owner", "accountant"];
const immutableStatuses = ["posted", "voided"];

function DetailItem({ label, value }: { label: string; value?: ReactNode }) {
  return (
    <div>
      <dt className="text-xs font-semibold uppercase text-slate-500">{label}</dt>
      <dd className="mt-1 text-sm text-slate-800">{value || "Not set"}</dd>
    </div>
  );
}

export default function TeacherPaymentDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const id = useRouteId(params);
  const queryClient = useQueryClient();
  const { hasRole } = useAuth();
  const canMutate = financialRoles.some((role) => hasRole(role));
  const { data: payment, error, isLoading, refetch } = useQuery({
    enabled: Boolean(id),
    queryKey: ["teacher-payments", id],
    queryFn: () => getTeacherPayment(id),
  });
  const approveMutation = useMutation({
    mutationFn: () => approveTeacherPayment(id),
    onSuccess: async (updatedPayment) => {
      queryClient.setQueryData(["teacher-payments", id], updatedPayment);
      await queryClient.invalidateQueries({ queryKey: ["teacher-payments"] });
      await refetch();
    },
  });
  const postMutation = useMutation({
    mutationFn: () => postTeacherPayment(id),
    onSuccess: async (updatedPayment) => {
      queryClient.setQueryData(["teacher-payments", id], updatedPayment);
      await queryClient.invalidateQueries({ queryKey: ["teacher-payments"] });
      await refetch();
    },
  });

  const canApprove = Boolean(payment && canMutate && ["draft", "submitted"].includes(payment.status));
  const canPost = Boolean(payment && canMutate && payment.status === "approved");
  const isImmutable = Boolean(payment && immutableStatuses.includes(payment.status));

  return (
    <div className="space-y-5">
      <PageHeader
        actions={
          <>
            {canApprove ? (
              <Button isLoading={approveMutation.isPending} onClick={() => approveMutation.mutate()} type="button">
                Approve and post
              </Button>
            ) : null}
            {canPost ? (
              <Button isLoading={postMutation.isPending} onClick={() => postMutation.mutate()} type="button">
                Post payment
              </Button>
            ) : null}
            <Link className="rounded-md border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50" href="/dashboard/payroll/payments">
              Back to teacher payments
            </Link>
          </>
        }
        description="Teacher payment profile. Approval and posting use secured backend payroll workflow APIs."
        title={payment?.voucher_number || payment?.draft_voucher_number || "Teacher payment"}
      />

      {isLoading ? <LoadingState label="Loading teacher payment..." /> : null}
      {error ? <ErrorState message={error instanceof Error ? error.message : undefined} /> : null}
      {approveMutation.isError ? (
        <ErrorState
          message={approveMutation.error instanceof Error ? approveMutation.error.message : "Unable to approve teacher payment."}
          title="Approval failed"
        />
      ) : null}
      {postMutation.isError ? (
        <ErrorState
          message={postMutation.error instanceof Error ? postMutation.error.message : "Unable to post teacher payment."}
          title="Posting failed"
        />
      ) : null}
      {approveMutation.isSuccess ? (
        <div className="rounded-lg border border-green-100 bg-green-50 p-4 text-sm font-medium text-green-700">
          Teacher payment approved and posted.
        </div>
      ) : null}
      {postMutation.isSuccess ? (
        <div className="rounded-lg border border-green-100 bg-green-50 p-4 text-sm font-medium text-green-700">
          Teacher payment posted.
        </div>
      ) : null}
      {isImmutable ? (
        <div className="rounded-lg border border-slate-200 bg-white p-4 text-sm text-slate-600">
          This teacher payment is {payment?.status} and is read-only. Changes, voids, and accounting entries must use dedicated backend workflows.
        </div>
      ) : null}

      {payment ? (
        <section className="grid gap-4 lg:grid-cols-3">
          <article className="rounded-lg bg-white p-5 shadow-[0_2px_18px_rgba(38,43,64,0.08)] lg:col-span-2">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h2 className="text-lg font-semibold text-[#262B40]">{payment.voucher_number || payment.draft_voucher_number || payment.id}</h2>
                <p className="mt-1 text-sm text-slate-500">Teacher {payment.teacher}</p>
              </div>
              <StatusBadge status={payment.status} />
            </div>
            <dl className="mt-6 grid gap-4 sm:grid-cols-2">
              <DetailItem label="Payment date" value={payment.payment_date_ad} />
              <DetailItem label="Method" value={payment.payment_method} />
              <DetailItem label="Amount" value={<MoneyDisplay amount={payment.amount} />} />
              <DetailItem label="Deduction" value={<MoneyDisplay amount={payment.deduction_amount} />} />
              <DetailItem label="Net paid" value={<MoneyDisplay amount={payment.net_paid_amount} />} />
              <DetailItem label="Reference" value={payment.reference_number} />
              <DetailItem label="Batch ID" value={payment.payment_batch} />
              <DetailItem label="Posted at" value={payment.posted_at} />
            </dl>
          </article>
          <article className="rounded-lg bg-white p-5 shadow-[0_2px_18px_rgba(38,43,64,0.08)]">
            <h2 className="text-base font-semibold text-[#262B40]">Accounting Boundary</h2>
            <p className="mt-4 text-sm leading-6 text-slate-700">
              The frontend does not calculate ledger effects. Approval and posting send this payment to backend payroll services, which validate allocations and post accounting entries.
            </p>
          </article>
          <article className="rounded-lg bg-white p-5 shadow-[0_2px_18px_rgba(38,43,64,0.08)] lg:col-span-3">
            <h2 className="text-base font-semibold text-[#262B40]">Notes</h2>
            <p className="mt-4 text-sm leading-6 text-slate-700">{payment.notes || payment.void_reason || "No notes recorded."}</p>
          </article>
        </section>
      ) : null}

      {!isLoading && !error && !payment ? <EmptyState title="Teacher payment not found" /> : null}
    </div>
  );
}
