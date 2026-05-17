"use client";

import { FormEvent } from "react";
import Link from "next/link";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState } from "@/components/ui/ErrorState";
import { LoadingState } from "@/components/ui/LoadingState";
import { MoneyDisplay } from "@/components/ui/MoneyDisplay";
import { PageHeader } from "@/components/ui/PageHeader";
import { SimpleTable } from "@/components/ui/SimpleTable";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { TextInput } from "@/components/ui/TextInput";
import { useAuth } from "@/hooks/useAuth";
import { cancelAcademicRollover, executeAcademicRollover, getAcademicRollover, getAcademicRolloverSummary, validateAcademicRollover } from "@/lib/academic";
import { listJournalEntries } from "@/lib/accounting";
import type { JournalEntry } from "@/types/accounting";
import type { Role } from "@/types/auth";

const rolloverRoles: Role[] = ["super_admin", "institute_owner", "accountant"];

function rolloverJournalKind(entry: JournalEntry) {
  if (entry.source_number.startsWith("opening")) return "Opening";
  if (entry.source_number.startsWith("closing")) return "Closing";
  return "Rollover";
}

export default function AcademicRolloverDetailPage({ params }: { params: { id: string } }) {
  const queryClient = useQueryClient();
  const { hasRole } = useAuth();
  const canMutate = rolloverRoles.some((role) => hasRole(role));
  const { data: rollover, error, isLoading } = useQuery({
    queryKey: ["academic-rollovers", params.id],
    queryFn: () => getAcademicRollover(params.id),
  });
  const summary = useQuery({
    queryKey: ["academic-rollovers", params.id, "summary"],
    queryFn: () => getAcademicRolloverSummary(params.id),
  });
  const generatedJournals = useQuery({
    queryKey: ["academic-rollovers", params.id, "generated-journals"],
    queryFn: () =>
      listJournalEntries({
        source_app: "academic",
        source_model: "AcademicYearRollover",
        source_object_id: params.id,
        source_type: "system",
      }),
  });
  const refresh = () => {
    void queryClient.invalidateQueries({ queryKey: ["academic-rollovers", params.id] });
    void queryClient.invalidateQueries({ queryKey: ["academic-rollovers", params.id, "summary"] });
    void queryClient.invalidateQueries({ queryKey: ["academic-rollovers", params.id, "generated-journals"] });
  };
  const validateMutation = useMutation({ mutationFn: () => validateAcademicRollover(params.id), onSuccess: refresh });
  const cancelMutation = useMutation({ mutationFn: () => cancelAcademicRollover(params.id, { reason: "Cancelled from dashboard" }), onSuccess: refresh });
  const executeMutation = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Parameters<typeof executeAcademicRollover>[1] }) =>
      executeAcademicRollover(id, payload),
    onSuccess: refresh,
  });
  const showValidate = canMutate && rollover && ["draft", "validating", "failed"].includes(rollover.status);
  const showExecute = canMutate && rollover && ["draft", "ready"].includes(rollover.status);
  const showCancel = canMutate && rollover && !["executed", "cancelled"].includes(rollover.status);

  function handleExecute(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    executeMutation.mutate({
      id: params.id,
      payload: {
        hard_close: formData.get("hard_close") === "on",
        new_year_data: {
          name: String(formData.get("name") ?? ""),
          bs_start_year: Number(formData.get("bs_start_year") ?? 0),
          bs_end_year: Number(formData.get("bs_end_year") ?? 0),
          bs_start_date: String(formData.get("bs_start_date") ?? ""),
          bs_end_date: String(formData.get("bs_end_date") ?? ""),
          ad_start_date: String(formData.get("ad_start_date") ?? ""),
          ad_end_date: String(formData.get("ad_end_date") ?? ""),
          notes: String(formData.get("notes") ?? ""),
        },
      },
    });
  }

  return (
    <div className="space-y-5">
      <PageHeader
        actions={
          <div className="flex flex-wrap gap-2">
            {showValidate ? <Button isLoading={validateMutation.isPending} onClick={() => validateMutation.mutate()} type="button">Validate</Button> : null}
            {showCancel ? <Button isLoading={cancelMutation.isPending} onClick={() => cancelMutation.mutate()} type="button" variant="secondary">Cancel</Button> : null}
            <Link className="rounded-md border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50" href="/dashboard/academic-rollovers">
              Back to rollovers
            </Link>
          </div>
        }
        description="Execution posts closing and opening entries in the backend. Review carefully before running."
        title="Academic Rollover"
      />
      {isLoading || summary.isLoading ? <LoadingState label="Loading rollover..." /> : null}
      {error ? <ErrorState message={error instanceof Error ? error.message : undefined} /> : null}
      {validateMutation.isSuccess ? <p className="rounded-md bg-green-50 px-4 py-3 text-sm font-medium text-green-700">Rollover validated.</p> : null}
      {executeMutation.isSuccess ? <p className="rounded-md bg-green-50 px-4 py-3 text-sm font-medium text-green-700">Rollover executed.</p> : null}
      {cancelMutation.isSuccess ? <p className="rounded-md bg-green-50 px-4 py-3 text-sm font-medium text-green-700">Rollover cancelled.</p> : null}
      {validateMutation.isError || executeMutation.isError || cancelMutation.isError ? <ErrorState title="Rollover action failed" /> : null}
      {rollover ? (
        <>
          <article className="rounded-lg bg-white p-5 shadow-[0_2px_18px_rgba(38,43,64,0.08)]">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h2 className="text-lg font-semibold text-[#262B40]">{rollover.id}</h2>
                <p className="mt-1 text-sm text-slate-500">Source year: {rollover.from_academic_year}</p>
              </div>
              <StatusBadge status={rollover.status} />
            </div>
            <dl className="mt-6 grid gap-4 text-sm sm:grid-cols-2 lg:grid-cols-4">
              <div><dt className="font-semibold text-slate-500">Target year</dt><dd>{rollover.to_academic_year || "Not created"}</dd></div>
              <div><dt className="font-semibold text-slate-500">Trial balance</dt><dd>{rollover.trial_balance_validated ? "Validated" : "Pending"}</dd></div>
              <div><dt className="font-semibold text-slate-500">Closing entries</dt><dd>{rollover.revenue_expense_closing_completed ? "Posted" : "Pending"}</dd></div>
              <div><dt className="font-semibold text-slate-500">Opening entries</dt><dd>{rollover.opening_balances_posted ? "Posted" : "Pending"}</dd></div>
              <div><dt className="font-semibold text-slate-500">Executed at</dt><dd>{rollover.executed_at || "Not executed"}</dd></div>
              <div><dt className="font-semibold text-slate-500">Summary status</dt><dd>{summary.data?.status ?? rollover.status}</dd></div>
            </dl>
          </article>
          {showExecute ? (
            <form className="space-y-4 rounded-lg border border-red-100 bg-white p-5 shadow-[0_2px_18px_rgba(38,43,64,0.08)]" onSubmit={handleExecute}>
              <div>
                <h2 className="text-base font-semibold text-red-700">Execute rollover</h2>
                <p className="mt-1 text-sm text-red-600">High-risk action. Backend will validate trial balance and post closing/opening entries.</p>
              </div>
              <div className="grid gap-4 md:grid-cols-2">
                <TextInput label="New year name" name="name" required />
                <TextInput label="BS start year" name="bs_start_year" required type="number" />
                <TextInput label="BS end year" name="bs_end_year" required type="number" />
                <TextInput label="BS start date" name="bs_start_date" required />
                <TextInput label="BS end date" name="bs_end_date" required />
                <TextInput label="AD start date" name="ad_start_date" required type="date" />
                <TextInput label="AD end date" name="ad_end_date" required type="date" />
                <TextInput label="Notes" name="notes" />
              </div>
              <label className="flex items-center gap-2 text-sm font-medium text-slate-700">
                <input className="h-4 w-4" defaultChecked name="hard_close" type="checkbox" />
                Hard close outgoing year after execution
              </label>
              <Button isLoading={executeMutation.isPending} type="submit">Execute rollover</Button>
            </form>
          ) : null}
          <section className="space-y-3">
            <div>
              <h2 className="text-base font-semibold text-[#262B40]">Generated Journal Entries</h2>
              <p className="mt-1 text-sm text-slate-500">Read-only closing and opening entries linked to this rollover.</p>
            </div>
            {generatedJournals.isLoading ? <LoadingState label="Loading generated journals..." /> : null}
            {generatedJournals.isError ? <ErrorState message={generatedJournals.error instanceof Error ? generatedJournals.error.message : undefined} /> : null}
            {generatedJournals.data && generatedJournals.data.data.length > 0 ? (
              <SimpleTable
                columns={[
                  {
                    header: "Entry",
                    render: (entry) => (
                      <Link className="font-semibold text-[#2563EB] hover:underline" href={`/dashboard/accounting/journal-entries/${entry.id}`}>
                        {entry.entry_number}
                      </Link>
                    ),
                  },
                  { header: "Type", render: (entry) => rolloverJournalKind(entry) },
                  { header: "Date", render: (entry) => entry.entry_date_ad },
                  { header: "Status", render: (entry) => <StatusBadge status={entry.status} /> },
                  { header: "Description", render: (entry) => entry.description || entry.narration || "Not set" },
                  { header: "Debit", render: (entry) => <MoneyDisplay amount={entry.debit_total ?? "0.00"} /> },
                  { header: "Credit", render: (entry) => <MoneyDisplay amount={entry.credit_total ?? "0.00"} /> },
                ]}
                getRowKey={(entry) => entry.id}
                rows={generatedJournals.data.data}
              />
            ) : null}
            {generatedJournals.data && generatedJournals.data.data.length === 0 ? (
              <EmptyState title="No generated journal entries found" />
            ) : null}
          </section>
        </>
      ) : null}
      {!isLoading && !error && !rollover ? <EmptyState title="Rollover not found" /> : null}
    </div>
  );
}
