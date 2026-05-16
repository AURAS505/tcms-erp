"use client";

import Link from "next/link";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState } from "@/components/ui/ErrorState";
import { LoadingState } from "@/components/ui/LoadingState";
import { PageHeader } from "@/components/ui/PageHeader";
import { SearchInput } from "@/components/ui/SearchInput";
import { SimpleTable, type SimpleTableColumn } from "@/components/ui/SimpleTable";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { listJournalEntries } from "@/lib/accounting";
import type { JournalEntry } from "@/types/accounting";

const columns: SimpleTableColumn<JournalEntry>[] = [
  {
    header: "Entry",
    render: (entry) => (
      <Link className="font-semibold text-[#0948B3] hover:underline" href={`/dashboard/accounting/journal-entries/${entry.id}`}>
        {entry.entry_number}
      </Link>
    ),
  },
  { header: "Date", render: (entry) => entry.entry_date_ad },
  { header: "Description", render: (entry) => entry.description },
  { header: "Source", render: (entry) => entry.source_app || entry.source_type },
  { header: "Status", render: (entry) => <StatusBadge status={entry.status} /> },
];

export default function JournalEntriesPage() {
  const [search, setSearch] = useState("");
  const { data, error, isLoading } = useQuery({
    queryKey: ["journal-entries", search],
    queryFn: () => listJournalEntries(search),
  });

  return (
    <div className="space-y-5">
      <PageHeader
        actions={<SearchInput onChange={(event) => setSearch(event.target.value)} placeholder="Search journal entries" value={search} />}
        description="Read-only journal entries. Manual entry, approval, posting, and reversal workflows are not exposed here."
        title="Journal Entries"
      />

      {isLoading ? <LoadingState label="Loading journal entries..." /> : null}
      {error ? <ErrorState message={error instanceof Error ? error.message : undefined} /> : null}
      {data && data.data.length === 0 ? (
        <EmptyState message="No journal entries are available." title="No journal entries found" />
      ) : null}
      {data && data.data.length > 0 ? <SimpleTable columns={columns} getRowKey={(entry) => entry.id} rows={data.data} /> : null}
    </div>
  );
}
