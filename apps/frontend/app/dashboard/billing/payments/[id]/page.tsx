"use client";

import { use } from "react";
import type { ReactNode } from "react";
import Link from "next/link";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState } from "@/components/ui/ErrorState";
import { LoadingState } from "@/components/ui/LoadingState";
import { MoneyDisplay } from "@/components/ui/MoneyDisplay";
import { PageHeader } from "@/components/ui/PageHeader";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { useAuth } from "@/hooks/useAuth";
import { approveStudentPayment, getStudentPayment } from "@/lib/billing";
import type { Role } from "@/types/auth";

const approverRoles: Role[] = ["super_admin", "institute_owner", "accountant"];
const immutableStatuses = ["posted", "voided", "refunded"];

function DetailItem({ label, value }: { label: string; value?: ReactNode }) {
  return (
    <div>
      <dt className="text-xs font-semibold uppercase text-slate-500">{label}</dt>
      <dd className="mt-1 text-sm text-slate-800">{value || "Not set"}</dd>
    </div>
  );
}

export default function PaymentDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const queryClient = useQueryClient();
  const { hasRole } = useAuth();
  const canApprove = approverRoles.some((role) => hasRole(role));
  const { data: payment, error, isLoading, refetch } = useQuery({
    queryKey: ["student-payments", id],
    queryFn: () => getStudentPayment(id),
  });
  const approveMutation = useMutation({
    mutationFn: () => approveStudentPayment(id),
    onSuccess: async (updatedPayment) => {
      queryClient.setQueryData(["student-payments", id], updatedPayment);
      await queryClient.invalidateQueries({ queryKey: ["student-payments"] });
      await refetch();
    },
  });

  const canShowApprove = Boolean(payment && canApprove && ["draft", "submitted"].includes(payment.status));
  const isImmutable = Boolean(payment && immutableStatuses.includes(payment.status));

  return (
    <div className="space-y-5">
      <PageHeader
        actions={
          <>
            {canShowApprove ? (
              <Button isLoading={approveMutation.isPending} onClick={() => approveMutation.mutate()} type="button">
                Approve and post
              </Button>
            ) : null}
            <Link className="rounded-md border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50" href="/dashboard/billing/payments">
              Back to payments
            </Link>
          </>
        }
        description="Payment profile. Approval and posting run through secured backend workflow APIs."
        title={payment?.receipt_number || payment?.draft_receipt_number || "Payment"}
      />

      {isLoading ? <LoadingState label="Loading payment..." /> : null}
      {error ? <ErrorState message={error instanceof Error ? error.message : undefined} /> : null}
      {approveMutation.isError ? (
        <ErrorState
          message={approveMutation.error instanceof Error ? approveMutation.error.message : "Unable to approve payment."}
          title="Approval failed"
        />
      ) : null}
      {approveMutation.isSuccess ? (
        <div className="rounded-lg border border-green-100 bg-green-50 p-4 text-sm font-medium text-green-700">
          Payment approved and posted.
        </div>
      ) : null}
      {isImmutable ? (
        <div className="rounded-lg border border-slate-200 bg-white p-4 text-sm text-slate-600">
          This payment is {payment?.status} and is read-only. Changes, voids, refunds, and accounting entries must use
          dedicated backend workflows.
        </div>
      ) : null}

      {payment ? (
        <section className="grid gap-4 lg:grid-cols-3">
          <article className="rounded-lg bg-white p-5 shadow-[0_2px_18px_rgba(38,43,64,0.08)] lg:col-span-2">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h2 className="text-lg font-semibold text-[#262B40]">{payment.receipt_number || payment.draft_receipt_number || payment.id}</h2>
                <p className="mt-1 text-sm text-slate-500">Student {payment.student}</p>
              </div>
              <StatusBadge status={payment.status} />
            </div>
            <dl className="mt-6 grid gap-4 sm:grid-cols-2">
              <DetailItem label="Payment date" value={payment.payment_date_ad} />
              <DetailItem label="Method" value={payment.payment_method} />
              <DetailItem label="Amount" value={<MoneyDisplay amount={payment.amount} />} />
              <DetailItem label="Discount" value={<MoneyDisplay amount={payment.discount_amount} />} />
              <DetailItem label="Fine" value={<MoneyDisplay amount={payment.fine_amount} />} />
              <DetailItem label="Net received" value={<MoneyDisplay amount={payment.net_received_amount} />} />
              <DetailItem label="Reference" value={payment.reference_number} />
              <DetailItem label="Advance payment" value={payment.is_advance_payment ? "Yes" : "No"} />
            </dl>
          </article>
          <article className="rounded-lg bg-white p-5 shadow-[0_2px_18px_rgba(38,43,64,0.08)]">
            <h2 className="text-base font-semibold text-[#262B40]">Accounting Boundary</h2>
            <p className="mt-4 text-sm leading-6 text-slate-700">
              The frontend does not calculate ledger effects. Approval sends the payment to the backend workflow, which
              validates allocations, assigns receipt numbers, and posts accounting entries.
            </p>
          </article>
          <article className="rounded-lg bg-white p-5 shadow-[0_2px_18px_rgba(38,43,64,0.08)] lg:col-span-3">
            <h2 className="text-base font-semibold text-[#262B40]">Notes</h2>
            <p className="mt-4 text-sm leading-6 text-slate-700">{payment.notes || payment.void_reason || "No notes recorded."}</p>
          </article>
        </section>
      ) : null}

      {!isLoading && !error && !payment ? <EmptyState title="Payment not found" /> : null}
    </div>
  );
}
