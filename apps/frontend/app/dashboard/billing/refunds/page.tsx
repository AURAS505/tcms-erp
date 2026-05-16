"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState } from "@/components/ui/ErrorState";
import { LoadingState } from "@/components/ui/LoadingState";
import { MoneyDisplay } from "@/components/ui/MoneyDisplay";
import { PageHeader } from "@/components/ui/PageHeader";
import { SearchInput } from "@/components/ui/SearchInput";
import { SimpleTable, type SimpleTableColumn } from "@/components/ui/SimpleTable";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { useAuth } from "@/hooks/useAuth";
import { approveStudentRefund, listStudentRefunds, payStudentRefund } from "@/lib/billing";
import type { Role } from "@/types/auth";
import type { StudentRefund } from "@/types/billing";

const financialRoles: Role[] = ["super_admin", "institute_owner", "accountant"];

export default function StudentRefundsPage() {
  const [search, setSearch] = useState("");
  const [message, setMessage] = useState("");
  const queryClient = useQueryClient();
  const { hasRole } = useAuth();
  const canMutate = financialRoles.some((role) => hasRole(role));
  const { data, error, isLoading } = useQuery({
    queryKey: ["student-refunds", search],
    queryFn: () => listStudentRefunds(search),
  });
  const refreshRefunds = () => queryClient.invalidateQueries({ queryKey: ["student-refunds"] });
  const approveMutation = useMutation({
    mutationFn: approveStudentRefund,
    onSuccess: () => {
      setMessage("Refund approved.");
      refreshRefunds();
    },
  });
  const payMutation = useMutation({
    mutationFn: payStudentRefund,
    onSuccess: () => {
      setMessage("Refund paid.");
      refreshRefunds();
    },
  });

  const columns: SimpleTableColumn<StudentRefund>[] = [
    { header: "Voucher", render: (refund) => refund.refund_voucher_number || refund.id },
    { header: "Student", render: (refund) => refund.student },
    { header: "Amount", render: (refund) => <MoneyDisplay amount={refund.refund_amount} /> },
    { header: "Status", render: (refund) => <StatusBadge status={refund.status} /> },
    {
      header: "Action",
      render: (refund) => {
        if (!canMutate || refund.status === "paid" || refund.status === "cancelled") {
          return <span className="text-xs font-medium text-slate-500">Read-only</span>;
        }
        if (refund.status === "approved") {
          return (
            <Button
              aria-label="Pay refund"
              className="min-h-8 px-3 py-1.5"
              isLoading={payMutation.isPending && payMutation.variables === refund.id}
              onClick={() => payMutation.mutate(refund.id)}
              type="button"
            >
              Pay
            </Button>
          );
        }
        if (refund.status === "draft" || refund.status === "pending_approval") {
          return (
            <Button
              aria-label="Approve refund"
              className="min-h-8 px-3 py-1.5"
              isLoading={approveMutation.isPending && approveMutation.variables === refund.id}
              onClick={() => approveMutation.mutate(refund.id)}
              type="button"
            >
              Approve
            </Button>
          );
        }
        return <span className="text-xs font-medium text-slate-500">Read-only</span>;
      },
    },
  ];

  return (
    <div className="space-y-5">
      <PageHeader
        actions={<SearchInput onChange={(event) => setSearch(event.target.value)} placeholder="Search refunds" value={search} />}
        description="Read-only refund visibility with service-backed approval and advance refund payment."
        title="Student Refunds"
      />
      <p className="rounded-md bg-amber-50 px-3 py-2 text-sm text-amber-800">
        Recognized-revenue refunds may be blocked by backend policy; advance-backed refunds can be approved and paid here.
      </p>
      {message ? <p className="rounded-md bg-green-50 px-3 py-2 text-sm font-medium text-green-700">{message}</p> : null}
      {approveMutation.error ? <ErrorState message={approveMutation.error.message} /> : null}
      {payMutation.error ? <ErrorState message={payMutation.error.message} /> : null}
      {isLoading ? <LoadingState label="Loading refunds..." /> : null}
      {error ? <ErrorState message={error instanceof Error ? error.message : undefined} /> : null}
      {data && data.data.length === 0 ? <EmptyState message="No refunds are available." title="No refunds found" /> : null}
      {data && data.data.length > 0 ? <SimpleTable columns={columns} getRowKey={(refund) => refund.id} rows={data.data} /> : null}
    </div>
  );
}
