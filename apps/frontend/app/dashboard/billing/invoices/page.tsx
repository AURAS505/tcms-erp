"use client";

import Link from "next/link";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState } from "@/components/ui/ErrorState";
import { LoadingState } from "@/components/ui/LoadingState";
import { MoneyDisplay } from "@/components/ui/MoneyDisplay";
import { PageHeader } from "@/components/ui/PageHeader";
import { SearchInput } from "@/components/ui/SearchInput";
import { SimpleTable, type SimpleTableColumn } from "@/components/ui/SimpleTable";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { listInvoices } from "@/lib/billing";
import type { StudentInvoice } from "@/types/billing";

const columns: SimpleTableColumn<StudentInvoice>[] = [
  {
    header: "Invoice",
    render: (invoice) => (
      <Link className="font-semibold text-[#0948B3] hover:underline" href={`/dashboard/billing/invoices/${invoice.id}`}>
        {invoice.invoice_number}
      </Link>
    ),
  },
  { header: "Student", render: (invoice) => invoice.student },
  { header: "Invoice date", render: (invoice) => invoice.invoice_date_ad },
  { header: "Total", render: (invoice) => <MoneyDisplay amount={invoice.total_amount} /> },
  { header: "Balance", render: (invoice) => <MoneyDisplay amount={invoice.balance_amount} /> },
  { header: "Status", render: (invoice) => <StatusBadge status={invoice.status} /> },
];

export default function InvoicesPage() {
  const [search, setSearch] = useState("");
  const { data, error, isLoading } = useQuery({
    queryKey: ["invoices", search],
    queryFn: () => listInvoices(search),
  });

  return (
    <div className="space-y-5">
      <PageHeader
        actions={<SearchInput onChange={(event) => setSearch(event.target.value)} placeholder="Search invoices" value={search} />}
        description="Read-only student invoices. Posting, voiding, and collection workflows are not exposed here."
        title="Invoices"
      />

      {isLoading ? <LoadingState label="Loading invoices..." /> : null}
      {error ? <ErrorState message={error instanceof Error ? error.message : undefined} /> : null}
      {data && data.data.length === 0 ? (
        <EmptyState message="No invoices are available for your current branch context." title="No invoices found" />
      ) : null}
      {data && data.data.length > 0 ? <SimpleTable columns={columns} getRowKey={(invoice) => invoice.id} rows={data.data} /> : null}
    </div>
  );
}
