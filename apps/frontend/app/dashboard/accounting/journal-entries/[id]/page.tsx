"use client";

import type { ReactNode } from "react";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState } from "@/components/ui/ErrorState";
import { LoadingState } from "@/components/ui/LoadingState";
import { MoneyDisplay } from "@/components/ui/MoneyDisplay";
import { PageHeader } from "@/components/ui/PageHeader";
import { SimpleTable, type SimpleTableColumn } from "@/components/ui/SimpleTable";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { getJournalEntry } from "@/lib/accounting";
import type { JournalEntryLine } from "@/types/accounting";

function DetailItem({ label, value }: { label: string; value?: ReactNode }) {
  return (
    <div>
      <dt className="text-xs font-semibold uppercase text-slate-500">{label}</dt>
      <dd className="mt-1 text-sm text-slate-800">{value || "Not set"}</dd>
    </div>
  );
}

const lineColumns: SimpleTableColumn<JournalEntryLine>[] = [
  { header: "Account", render: (line) => line.account },
  { header: "Description", render: (line) => line.description || "Not set" },
  { header: "Debit", render: (line) => <MoneyDisplay amount={line.debit_amount} /> },
  { header: "Credit", render: (line) => <MoneyDisplay amount={line.credit_amount} /> },
];

export default function JournalEntryDetailPage({ params }: { params: { id: string } }) {
  const { data: entry, error, isLoading } = useQuery({
    queryKey: ["journal-entries", params.id],
    queryFn: () => getJournalEntry(params.id),
  });

  return (
    <div className="space-y-5">
      <PageHeader
        actions={
          <Link className="rounded-md border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50" href="/dashboard/accounting/journal-entries">
            Back to journal entries
          </Link>
        }
        description="Read-only journal entry profile. Approval, posting, reversal, and deletion workflows are not exposed here."
        title={entry?.entry_number ?? "Journal entry"}
      />

      {isLoading ? <LoadingState label="Loading journal entry..." /> : null}
      {error ? <ErrorState message={error instanceof Error ? error.message : undefined} /> : null}

      {entry ? (
        <section className="space-y-4">
          <article className="rounded-lg bg-white p-5 shadow-[0_2px_18px_rgba(38,43,64,0.08)]">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h2 className="text-lg font-semibold text-[#262B40]">{entry.description}</h2>
                <p className="mt-1 text-sm text-slate-500">{entry.entry_date_ad}</p>
              </div>
              <StatusBadge status={entry.status} />
            </div>
            <dl className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              <DetailItem label="Source" value={entry.source_app || entry.source_type} />
              <DetailItem label="Source number" value={entry.source_number} />
              <DetailItem label="Posting date" value={entry.posting_date_ad} />
              <DetailItem label="Posted at" value={entry.posted_at} />
            </dl>
            <p className="mt-6 text-sm leading-6 text-slate-700">{entry.narration || "No narration recorded."}</p>
          </article>

          {entry.lines && entry.lines.length > 0 ? (
            <SimpleTable columns={lineColumns} getRowKey={(line) => line.id} rows={entry.lines} />
          ) : (
            <EmptyState
              message="Journal lines are available through the journal-entry-lines endpoint; embedded line details are not included in this response."
              title="No embedded journal lines"
            />
          )}
        </section>
      ) : null}

      {!isLoading && !error && !entry ? <EmptyState title="Journal entry not found" /> : null}
    </div>
  );
}
