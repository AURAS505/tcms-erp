"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState } from "@/components/ui/ErrorState";
import { LoadingState } from "@/components/ui/LoadingState";
import { PageHeader } from "@/components/ui/PageHeader";
import { SearchInput } from "@/components/ui/SearchInput";
import { SimpleTable, type SimpleTableColumn } from "@/components/ui/SimpleTable";
import { listAccountingDocuments } from "@/lib/accounting";
import type { AccountingDocument } from "@/types/accounting";

const formatLabel = (value: string) =>
  value
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");

const columns: SimpleTableColumn<AccountingDocument>[] = [
  { header: "Reference", render: (document) => document.reference_number || document.id },
  { header: "Type", render: (document) => formatLabel(document.document_type) },
  { header: "Journal entry", render: (document) => document.journal_entry || "Not linked" },
  { header: "Description", render: (document) => document.description || "Not set" },
];

export default function AccountingDocumentsPage() {
  const [search, setSearch] = useState("");
  const { data, error, isLoading } = useQuery({
    queryKey: ["accounting-documents", search],
    queryFn: () => listAccountingDocuments(search),
  });

  return (
    <div className="space-y-5">
      <PageHeader
        actions={<SearchInput onChange={(event) => setSearch(event.target.value)} placeholder="Search accounting documents" value={search} />}
        description="Read-only accounting documents. Upload, replacement, and deletion workflows are not exposed here."
        title="Accounting Documents"
      />

      {isLoading ? <LoadingState label="Loading accounting documents..." /> : null}
      {error ? <ErrorState message={error instanceof Error ? error.message : undefined} /> : null}
      {data && data.data.length === 0 ? (
        <EmptyState message="No accounting documents are available." title="No accounting documents found" />
      ) : null}
      {data && data.data.length > 0 ? <SimpleTable columns={columns} getRowKey={(document) => document.id} rows={data.data} /> : null}
    </div>
  );
}
