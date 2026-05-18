"use client";
import Link from "next/link";
import { useRouteId } from "@/hooks/useRouteId";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState } from "@/components/ui/ErrorState";
import { LoadingState } from "@/components/ui/LoadingState";
import { MoneyDisplay } from "@/components/ui/MoneyDisplay";
import { DetailCard } from "@/components/ui/DetailCard";
import { DetailGrid, DetailItem } from "@/components/ui/DetailGrid";
import { PageHeader } from "@/components/ui/PageHeader";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { WarningPanel } from "@/components/ui/WarningPanel";
import { useAuth } from "@/hooks/useAuth";
import { approveTeacherPayment, getTeacherPayment, postTeacherPayment } from "@/lib/payroll";
import type { Role } from "@/types/auth";

const financialRoles: Role[] = ["super_admin", "institute_owner", "accountant"];
const immutableStatuses = ["posted", "voided"];

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
        <WarningPanel tone="success">Teacher payment approved and posted.</WarningPanel>
      ) : null}
      {postMutation.isSuccess ? (
        <WarningPanel tone="success">Teacher payment posted.</WarningPanel>
      ) : null}
      {isImmutable ? (
        <WarningPanel tone="neutral" title="Read-only teacher payment">
          This teacher payment is {payment?.status} and is read-only. Changes, voids, and accounting entries must use dedicated backend workflows.
        </WarningPanel>
      ) : null}

      {payment ? (
        <section className="grid gap-4 lg:grid-cols-3">
          <DetailCard
            actions={<StatusBadge status={payment.status} />}
            className="lg:col-span-2"
            description={`Teacher ${payment.teacher}`}
            title={payment.voucher_number || payment.draft_voucher_number || payment.id}
          >
            <DetailGrid>
              <DetailItem label="Payment date" value={payment.payment_date_ad} />
              <DetailItem label="Method" value={payment.payment_method} />
              <DetailItem label="Amount" value={<MoneyDisplay amount={payment.amount} />} />
              <DetailItem label="Deduction" value={<MoneyDisplay amount={payment.deduction_amount} />} />
              <DetailItem label="Net paid" value={<MoneyDisplay amount={payment.net_paid_amount} />} />
              <DetailItem label="Reference" value={payment.reference_number} />
              <DetailItem label="Batch ID" value={payment.payment_batch} />
              <DetailItem label="Posted at" value={payment.posted_at} />
            </DetailGrid>
          </DetailCard>
          <DetailCard title="Accounting Boundary">
            <p className="mt-4 text-sm leading-6 text-slate-700">
              The frontend does not calculate ledger effects. Approval and posting send this payment to backend payroll services, which validate allocations and post accounting entries.
            </p>
          </DetailCard>
          <DetailCard className="lg:col-span-3" title="Notes">
            <p className="mt-4 text-sm leading-6 text-slate-700">{payment.notes || payment.void_reason || "No notes recorded."}</p>
          </DetailCard>
        </section>
      ) : null}

      {!isLoading && !error && !payment ? <EmptyState title="Teacher payment not found" /> : null}
    </div>
  );
}
