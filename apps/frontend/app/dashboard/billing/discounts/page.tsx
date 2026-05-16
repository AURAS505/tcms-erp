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
import { approveBillingDiscount, listBillingDiscounts } from "@/lib/billing";
import type { Role } from "@/types/auth";
import type { BillingDiscount } from "@/types/billing";

const financialRoles: Role[] = ["super_admin", "institute_owner", "accountant"];
const canApproveStatus = (status: string) => status === "draft" || status === "pending_approval";

export default function BillingDiscountsPage() {
  const [search, setSearch] = useState("");
  const [message, setMessage] = useState("");
  const queryClient = useQueryClient();
  const { hasRole } = useAuth();
  const canMutate = financialRoles.some((role) => hasRole(role));
  const { data, error, isLoading } = useQuery({
    queryKey: ["billing-discounts", search],
    queryFn: () => listBillingDiscounts(search),
  });
  const approveMutation = useMutation({
    mutationFn: approveBillingDiscount,
    onSuccess: () => {
      setMessage("Discount approved.");
      queryClient.invalidateQueries({ queryKey: ["billing-discounts"] });
    },
  });

  const columns: SimpleTableColumn<BillingDiscount>[] = [
    { header: "Student", render: (discount) => discount.student },
    { header: "Type", render: (discount) => discount.discount_type },
    { header: "Amount", render: (discount) => <MoneyDisplay amount={discount.discount_amount ?? "0.00"} /> },
    { header: "Status", render: (discount) => <StatusBadge status={discount.status} /> },
    {
      header: "Action",
      render: (discount) =>
        canMutate && canApproveStatus(discount.status) ? (
          <Button
            aria-label="Approve discount"
            className="min-h-8 px-3 py-1.5"
            isLoading={approveMutation.isPending && approveMutation.variables === discount.id}
            onClick={() => approveMutation.mutate(discount.id)}
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
        actions={<SearchInput onChange={(event) => setSearch(event.target.value)} placeholder="Search discounts" value={search} />}
        description="Read-only discounts with service-backed approval for financial roles."
        title="Billing Discounts"
      />
      {message ? <p className="rounded-md bg-green-50 px-3 py-2 text-sm font-medium text-green-700">{message}</p> : null}
      {approveMutation.error ? <ErrorState message={approveMutation.error.message} /> : null}
      {isLoading ? <LoadingState label="Loading discounts..." /> : null}
      {error ? <ErrorState message={error instanceof Error ? error.message : undefined} /> : null}
      {data && data.data.length === 0 ? <EmptyState message="No discounts are available." title="No discounts found" /> : null}
      {data && data.data.length > 0 ? <SimpleTable columns={columns} getRowKey={(discount) => discount.id} rows={data.data} /> : null}
    </div>
  );
}
