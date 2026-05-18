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
import { approveStudentPayment, getStudentPayment } from "@/lib/billing";
import type { Role } from "@/types/auth";

const approverRoles: Role[] = ["super_admin", "institute_owner", "accountant"];
const immutableStatuses = ["posted", "voided", "refunded"];

export default function PaymentDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const id = useRouteId(params);
  const queryClient = useQueryClient();
  const { hasRole } = useAuth();
  const canApprove = approverRoles.some((role) => hasRole(role));
  const { data: payment, error, isLoading, refetch } = useQuery({
    enabled: Boolean(id),
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
        <WarningPanel tone="success">Payment approved and posted.</WarningPanel>
      ) : null}
      {isImmutable ? (
        <WarningPanel tone="neutral" title="Read-only payment">
          This payment is {payment?.status} and is read-only. Changes, voids, refunds, and accounting entries must use
          dedicated backend workflows.
        </WarningPanel>
      ) : null}

      {payment ? (
        <section className="grid gap-4 lg:grid-cols-3">
          <DetailCard
            actions={<StatusBadge status={payment.status} />}
            className="lg:col-span-2"
            description={`Student ${payment.student}`}
            title={payment.receipt_number || payment.draft_receipt_number || payment.id}
          >
            <DetailGrid>
              <DetailItem label="Payment date" value={payment.payment_date_ad} />
              <DetailItem label="Method" value={payment.payment_method} />
              <DetailItem label="Amount" value={<MoneyDisplay amount={payment.amount} />} />
              <DetailItem label="Discount" value={<MoneyDisplay amount={payment.discount_amount} />} />
              <DetailItem label="Fine" value={<MoneyDisplay amount={payment.fine_amount} />} />
              <DetailItem label="Net received" value={<MoneyDisplay amount={payment.net_received_amount} />} />
              <DetailItem label="Reference" value={payment.reference_number} />
              <DetailItem label="Advance payment" value={payment.is_advance_payment ? "Yes" : "No"} />
            </DetailGrid>
          </DetailCard>
          <DetailCard title="Accounting Boundary">
            <p className="mt-4 text-sm leading-6 text-slate-700">
              The frontend does not calculate ledger effects. Approval sends the payment to the backend workflow, which
              validates allocations, assigns receipt numbers, and posts accounting entries.
            </p>
          </DetailCard>
          <DetailCard className="lg:col-span-3" title="Notes">
            <p className="mt-4 text-sm leading-6 text-slate-700">{payment.notes || payment.void_reason || "No notes recorded."}</p>
          </DetailCard>
        </section>
      ) : null}

      {!isLoading && !error && !payment ? <EmptyState title="Payment not found" /> : null}
    </div>
  );
}
