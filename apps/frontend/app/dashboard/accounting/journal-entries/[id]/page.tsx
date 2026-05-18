"use client";

import { FormEvent, use } from "react";
import type { ReactNode } from "react";
import Link from "next/link";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState } from "@/components/ui/ErrorState";
import { LoadingState } from "@/components/ui/LoadingState";
import { MoneyDisplay } from "@/components/ui/MoneyDisplay";
import { PageHeader } from "@/components/ui/PageHeader";
import { SimpleTable, type SimpleTableColumn } from "@/components/ui/SimpleTable";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { TextInput } from "@/components/ui/TextInput";
import { useAuth } from "@/hooks/useAuth";
import {
  approveJournalEntry,
  attachAccountingDocument,
  getJournalEntry,
  listJournalEntryLines,
  postJournalEntry,
  reverseJournalEntry,
} from "@/lib/accounting";
import type { Role } from "@/types/auth";
import type { AccountingDocumentInput, JournalEntry, JournalEntryLine } from "@/types/accounting";

const accountingRoles: Role[] = ["super_admin", "institute_owner", "accountant"];
const immutableStatuses: JournalEntry["status"][] = ["posted", "reversed", "void"];

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

const documentTypeOptions = [
  { label: "Voucher", value: "voucher" },
  { label: "Receipt", value: "receipt" },
  { label: "Invoice", value: "invoice" },
  { label: "Contract", value: "contract" },
  { label: "Bank statement", value: "bank_statement" },
  { label: "Supporting document", value: "supporting_document" },
  { label: "Other", value: "other" },
];

export default function JournalEntryDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const queryClient = useQueryClient();
  const { hasRole } = useAuth();
  const canMutate = accountingRoles.some((role) => hasRole(role));
  const { data: entry, error, isLoading } = useQuery({
    queryKey: ["journal-entries", id],
    queryFn: () => getJournalEntry(id),
  });
  const lines = useQuery({
    enabled: Boolean(entry?.entry_number),
    queryKey: ["journal-entry-lines", entry?.entry_number],
    queryFn: () => listJournalEntryLines(entry?.entry_number ?? ""),
  });

  const refreshEntry = () => {
    void queryClient.invalidateQueries({ queryKey: ["journal-entries", id] });
    void queryClient.invalidateQueries({ queryKey: ["journal-entry-lines", entry?.entry_number] });
  };
  const approveMutation = useMutation({ mutationFn: () => approveJournalEntry(id), onSuccess: refreshEntry });
  const postMutation = useMutation({ mutationFn: () => postJournalEntry(id), onSuccess: refreshEntry });
  const reverseMutation = useMutation({
    mutationFn: () => reverseJournalEntry(id, { narration: `Reversal of ${entry?.entry_number ?? "journal entry"}` }),
    onSuccess: refreshEntry,
  });
  const documentMutation = useMutation({
    mutationFn: (payload: AccountingDocumentInput) => attachAccountingDocument(id, payload),
  });

  const showApprove = canMutate && entry && ["draft", "pending_approval"].includes(entry.status);
  const showPost = canMutate && entry?.status === "approved";
  const showReverse = canMutate && entry?.status === "posted";
  const isReadOnly = entry ? immutableStatuses.includes(entry.status) : false;

  function handleDocumentSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const formData = new FormData(form);
    documentMutation.mutate(
      {
        document_type: String(formData.get("document_type") ?? ""),
        reference_number: String(formData.get("reference_number") ?? ""),
        description: String(formData.get("description") ?? ""),
      },
      {
        onSuccess: () => form.reset(),
      },
    );
  }

  return (
    <div className="space-y-5">
      <PageHeader
        actions={
          <div className="flex flex-wrap gap-2">
            {showApprove ? (
              <Button isLoading={approveMutation.isPending} onClick={() => approveMutation.mutate()} type="button">
                Approve journal
              </Button>
            ) : null}
            {showPost ? (
              <Button isLoading={postMutation.isPending} onClick={() => postMutation.mutate()} type="button">
                Post journal
              </Button>
            ) : null}
            {showReverse ? (
              <Button isLoading={reverseMutation.isPending} onClick={() => reverseMutation.mutate()} type="button" variant="secondary">
                Reverse journal
              </Button>
            ) : null}
            <Link className="rounded-md border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50" href="/dashboard/accounting/journal-entries">
              Back to journal entries
            </Link>
          </div>
        }
        description="Review journal lines and run approved accounting actions through backend workflows."
        title={entry?.entry_number ?? "Journal entry"}
      />

      {isLoading ? <LoadingState label="Loading journal entry..." /> : null}
      {error ? <ErrorState message={error instanceof Error ? error.message : undefined} /> : null}
      {approveMutation.isSuccess ? <p className="rounded-md bg-green-50 px-4 py-3 text-sm font-medium text-green-700">Journal entry approved.</p> : null}
      {postMutation.isSuccess ? <p className="rounded-md bg-green-50 px-4 py-3 text-sm font-medium text-green-700">Journal entry posted.</p> : null}
      {reverseMutation.isSuccess ? <p className="rounded-md bg-green-50 px-4 py-3 text-sm font-medium text-green-700">Journal entry reversed.</p> : null}
      {documentMutation.isSuccess ? <p className="rounded-md bg-green-50 px-4 py-3 text-sm font-medium text-green-700">Document reference added.</p> : null}
      {approveMutation.isError || postMutation.isError || reverseMutation.isError ? <ErrorState title="Journal action failed" /> : null}
      {documentMutation.isError ? (
        <ErrorState
          message={documentMutation.error instanceof Error ? documentMutation.error.message : "Unable to add document reference."}
          title="Document reference failed"
        />
      ) : null}

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
            {isReadOnly ? <p className="mt-4 rounded-md bg-slate-50 px-3 py-2 text-sm font-medium text-slate-600">This journal entry is {entry.status} and is read-only.</p> : null}
          </article>

          {lines.isLoading ? <LoadingState label="Loading journal lines..." /> : null}
          {lines.data && lines.data.data.length > 0 ? (
            <SimpleTable columns={lineColumns} getRowKey={(line) => line.id} rows={lines.data.data} />
          ) : (
            <EmptyState
              message="No journal lines were returned for this entry."
              title="No journal lines"
            />
          )}

          {canMutate ? (
            <form className="rounded-lg bg-white p-5 shadow-[0_2px_18px_rgba(38,43,64,0.08)]" onSubmit={handleDocumentSubmit}>
              <div className="mb-4">
                <h2 className="text-base font-semibold text-[#262B40]">Add Document Reference</h2>
                <p className="mt-1 text-sm text-slate-500">Metadata only. File upload is not enabled here.</p>
              </div>
              <fieldset className="grid gap-4 md:grid-cols-3" disabled={documentMutation.isPending}>
                <label className="block text-sm font-medium text-slate-700">
                  Document type
                  <select className="mt-2 w-full rounded-md border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm" name="document_type" required>
                    {documentTypeOptions.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </label>
                <TextInput label="Reference number" name="reference_number" placeholder="VCH-001" />
                <TextInput label="Description" name="description" placeholder="Supporting voucher reference" />
              </fieldset>
              <div className="mt-4 flex justify-end">
                <Button isLoading={documentMutation.isPending} type="submit" variant="secondary">
                  Add Document Reference
                </Button>
              </div>
            </form>
          ) : null}
        </section>
      ) : null}

      {!isLoading && !error && !entry ? <EmptyState title="Journal entry not found" /> : null}
    </div>
  );
}
