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
import { approveBillingFine, listBillingFines } from "@/lib/billing";
import type { Role } from "@/types/auth";
import type { BillingFine } from "@/types/billing";

const financialRoles: Role[] = ["super_admin", "institute_owner", "accountant"];
const canApproveStatus = (status: string) => status === "draft" || status === "pending_approval";

export default function BillingFinesPage() {
  const [search, setSearch] = useState("");
  const [message, setMessage] = useState("");
  const queryClient = useQueryClient();
  const { hasRole } = useAuth();
  const canMutate = financialRoles.some((role) => hasRole(role));
  const { data, error, isLoading } = useQuery({
    queryKey: ["billing-fines", search],
    queryFn: () => listBillingFines(search),
  });
  const approveMutation = useMutation({
    mutationFn: approveBillingFine,
    onSuccess: () => {
      setMessage("Fine approved.");
      queryClient.invalidateQueries({ queryKey: ["billing-fines"] });
    },
  });

  const columns: SimpleTableColumn<BillingFine>[] = [
    { header: "Student", render: (fine) => fine.student },
    { header: "Type", render: (fine) => fine.fine_type },
    { header: "Amount", render: (fine) => <MoneyDisplay amount={fine.amount} /> },
    { header: "Status", render: (fine) => <StatusBadge status={fine.status} /> },
    {
      header: "Action",
      render: (fine) =>
        canMutate && canApproveStatus(fine.status) ? (
          <Button
            aria-label="Approve fine"
            className="min-h-8 px-3 py-1.5"
            isLoading={approveMutation.isPending && approveMutation.variables === fine.id}
            onClick={() => approveMutation.mutate(fine.id)}
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
        actions={<SearchInput onChange={(event) => setSearch(event.target.value)} placeholder="Search fines" value={search} />}
        description="Read-only fines with service-backed approval for financial roles."
        title="Billing Fines"
      />
      {message ? <p className="rounded-md bg-green-50 px-3 py-2 text-sm font-medium text-green-700">{message}</p> : null}
      {approveMutation.error ? <ErrorState message={approveMutation.error.message} /> : null}
      {isLoading ? <LoadingState label="Loading fines..." /> : null}
      {error ? <ErrorState message={error instanceof Error ? error.message : undefined} /> : null}
      {data && data.data.length === 0 ? <EmptyState message="No fines are available." title="No fines found" /> : null}
      {data && data.data.length > 0 ? <SimpleTable columns={columns} getRowKey={(fine) => fine.id} rows={data.data} /> : null}
    </div>
  );
}
