"use client";

import { FormEvent, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState } from "@/components/ui/ErrorState";
import { LoadingState } from "@/components/ui/LoadingState";
import { MoneyDisplay } from "@/components/ui/MoneyDisplay";
import { PageHeader } from "@/components/ui/PageHeader";
import { SearchInput } from "@/components/ui/SearchInput";
import { SimpleTable, type SimpleTableColumn } from "@/components/ui/SimpleTable";
import { TextInput } from "@/components/ui/TextInput";
import { useAuth } from "@/hooks/useAuth";
import { applyAdvanceToDue, applyAdvanceToInvoice, listAdvanceBalances } from "@/lib/billing";
import type { Role } from "@/types/auth";
import type { StudentAdvanceBalance } from "@/types/billing";

const financialRoles: Role[] = ["super_admin", "institute_owner", "accountant"];

export default function AdvanceBalancesPage() {
  const [search, setSearch] = useState("");
  const [targetType, setTargetType] = useState<"due" | "invoice">("due");
  const [student, setStudent] = useState("");
  const [targetId, setTargetId] = useState("");
  const [amount, setAmount] = useState("");
  const [message, setMessage] = useState("");
  const queryClient = useQueryClient();
  const { hasRole } = useAuth();
  const canMutate = financialRoles.some((role) => hasRole(role));
  const { data, error, isLoading } = useQuery({
    queryKey: ["advance-balances", search],
    queryFn: () => listAdvanceBalances(search),
  });
  const applyToDueMutation = useMutation({ mutationFn: applyAdvanceToDue });
  const applyToInvoiceMutation = useMutation({ mutationFn: applyAdvanceToInvoice });
  const isApplying = applyToDueMutation.isPending || applyToInvoiceMutation.isPending;
  const mutationError = applyToDueMutation.error ?? applyToInvoiceMutation.error;

  const columns: SimpleTableColumn<StudentAdvanceBalance>[] = [
    { header: "Student", render: (balance) => balance.student },
    { header: "Received", render: (balance) => <MoneyDisplay amount={balance.received_amount} /> },
    { header: "Applied", render: (balance) => <MoneyDisplay amount={balance.applied_amount} /> },
    { header: "Refunded", render: (balance) => <MoneyDisplay amount={balance.refunded_amount} /> },
    { header: "Balance", render: (balance) => <MoneyDisplay amount={balance.balance_amount} /> },
  ];

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage("");
    if (targetType === "due") {
      await applyToDueMutation.mutateAsync({ student, due: targetId, amount });
    } else {
      await applyToInvoiceMutation.mutateAsync({ student, invoice: targetId, amount });
    }
    setTargetId("");
    setAmount("");
    setMessage("Advance applied.");
    queryClient.invalidateQueries({ queryKey: ["advance-balances"] });
  }

  return (
    <div className="space-y-5">
      <PageHeader
        actions={<SearchInput onChange={(event) => setSearch(event.target.value)} placeholder="Search advances" value={search} />}
        description="Read-only advance balances with service-backed application to dues or invoices."
        title="Advance Balances"
      />

      {canMutate ? (
        <form className="grid gap-3 rounded-lg bg-white p-4 shadow-[0_2px_18px_rgba(38,43,64,0.08)] md:grid-cols-5" onSubmit={onSubmit}>
          <label className="block text-sm font-medium text-slate-700">
            Target
            <select
              className="mt-2 block w-full rounded-md border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm text-slate-900"
              onChange={(event) => setTargetType(event.target.value as "due" | "invoice")}
              value={targetType}
            >
              <option value="due">Due</option>
              <option value="invoice">Invoice</option>
            </select>
          </label>
          <TextInput label="Student ID" onChange={(event) => setStudent(event.target.value)} required value={student} />
          <TextInput label={targetType === "due" ? "Due ID" : "Invoice ID"} onChange={(event) => setTargetId(event.target.value)} required value={targetId} />
          <TextInput label="Amount" min="0.01" onChange={(event) => setAmount(event.target.value)} required step="0.01" type="number" value={amount} />
          <div className="flex items-end">
            <Button className="w-full" isLoading={isApplying} type="submit">
              Apply
            </Button>
          </div>
        </form>
      ) : null}

      {message ? <p className="rounded-md bg-green-50 px-3 py-2 text-sm font-medium text-green-700">{message}</p> : null}
      {mutationError ? <ErrorState message={mutationError.message} /> : null}
      {isLoading ? <LoadingState label="Loading advance balances..." /> : null}
      {error ? <ErrorState message={error instanceof Error ? error.message : undefined} /> : null}
      {data && data.data.length === 0 ? <EmptyState message="No advance balances are available." title="No advances found" /> : null}
      {data && data.data.length > 0 ? <SimpleTable columns={columns} getRowKey={(balance) => balance.id} rows={data.data} /> : null}
    </div>
  );
}
