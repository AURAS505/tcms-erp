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
import { approveBillingWaiver, listBillingWaivers } from "@/lib/billing";
import type { Role } from "@/types/auth";
import type { BillingWaiver } from "@/types/billing";

const financialRoles: Role[] = ["super_admin", "institute_owner", "accountant"];
const canApproveStatus = (status: string) => status === "draft" || status === "pending_approval";

export default function BillingWaiversPage() {
  const [search, setSearch] = useState("");
  const [message, setMessage] = useState("");
  const queryClient = useQueryClient();
  const { hasRole } = useAuth();
  const canMutate = financialRoles.some((role) => hasRole(role));
  const { data, error, isLoading } = useQuery({
    queryKey: ["billing-waivers", search],
    queryFn: () => listBillingWaivers(search),
  });
  const approveMutation = useMutation({
    mutationFn: approveBillingWaiver,
    onSuccess: () => {
      setMessage("Waiver approved.");
      queryClient.invalidateQueries({ queryKey: ["billing-waivers"] });
    },
  });

  const columns: SimpleTableColumn<BillingWaiver>[] = [
    { header: "Student", render: (waiver) => waiver.student },
    { header: "Amount", render: (waiver) => <MoneyDisplay amount={waiver.waiver_amount} /> },
    { header: "Reason", render: (waiver) => waiver.reason },
    { header: "Status", render: (waiver) => <StatusBadge status={waiver.status} /> },
    {
      header: "Action",
      render: (waiver) =>
        canMutate && canApproveStatus(waiver.status) ? (
          <Button
            aria-label="Approve waiver"
            className="min-h-8 px-3 py-1.5"
            isLoading={approveMutation.isPending && approveMutation.variables === waiver.id}
            onClick={() => approveMutation.mutate(waiver.id)}
            type="button"
          >
            Approve
          </Button>
        ) : (
          <span className="text-xs font-medium text-slate-500">Read-only</span>
        ),
    },
  ];

  return (
    <div className="space-y-5">
      <PageHeader
        actions={<SearchInput onChange={(event) => setSearch(event.target.value)} placeholder="Search waivers" value={search} />}
        description="Read-only waivers and write-offs with service-backed approval for financial roles."
        title="Billing Waivers"
      />
      {message ? <p className="rounded-md bg-green-50 px-3 py-2 text-sm font-medium text-green-700">{message}</p> : null}
      {approveMutation.error ? <ErrorState message={approveMutation.error.message} /> : null}
      {isLoading ? <LoadingState label="Loading waivers..." /> : null}
      {error ? <ErrorState message={error instanceof Error ? error.message : undefined} /> : null}
      {data && data.data.length === 0 ? <EmptyState message="No waivers are available." title="No waivers found" /> : null}
      {data && data.data.length > 0 ? <SimpleTable columns={columns} getRowKey={(waiver) => waiver.id} rows={data.data} /> : null}
    </div>
  );
}
