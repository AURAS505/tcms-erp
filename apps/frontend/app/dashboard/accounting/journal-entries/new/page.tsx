"use client";

import { FormEvent, useMemo, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/Button";
import { ErrorState } from "@/components/ui/ErrorState";
import { ActionBar } from "@/components/ui/ActionBar";
import { FormCard } from "@/components/ui/FormCard";
import { LoadingState } from "@/components/ui/LoadingState";
import { MoneyDisplay } from "@/components/ui/MoneyDisplay";
import { PageHeader } from "@/components/ui/PageHeader";
import { TextInput } from "@/components/ui/TextInput";
import { WarningPanel } from "@/components/ui/WarningPanel";
import { useAuth } from "@/hooks/useAuth";
import { createManualJournalEntry, listAccounts } from "@/lib/accounting";
import { listAcademicPeriods, listAcademicYears, listBranches, listOrganizations } from "@/lib/lookups";
import type { Role } from "@/types/auth";
import type { ManualJournalCreateInput } from "@/types/accounting";

const accountingRoles: Role[] = ["super_admin", "institute_owner", "accountant"];

interface JournalLineRow {
  id: number;
  account: string;
  description: string;
  debit_amount: string;
  credit_amount: string;
}

const newLine = (id: number): JournalLineRow => ({
  id,
  account: "",
  description: "",
  debit_amount: "",
  credit_amount: "",
});

const amount = (value: string) => Number.parseFloat(value || "0") || 0;

function isQueryLoading(...states: { isLoading: boolean }[]) {
  return states.some((state) => state.isLoading);
}

export default function NewJournalEntryPage() {
  const router = useRouter();
  const { hasRole } = useAuth();
  const canMutate = accountingRoles.some((role) => hasRole(role));
  const [selectedAcademicYear, setSelectedAcademicYear] = useState("");
  const [lines, setLines] = useState<JournalLineRow[]>([newLine(1), newLine(2)]);

  const organizations = useQuery({ queryKey: ["journal-form-organizations"], queryFn: listOrganizations });
  const branches = useQuery({ queryKey: ["journal-form-branches"], queryFn: listBranches });
  const academicYears = useQuery({ queryKey: ["journal-form-academic-years"], queryFn: listAcademicYears });
  const academicPeriods = useQuery({ queryKey: ["journal-form-academic-periods"], queryFn: listAcademicPeriods });
  const accounts = useQuery({ queryKey: ["journal-form-accounts"], queryFn: () => listAccounts() });

  const createMutation = useMutation({
    mutationFn: createManualJournalEntry,
    onSuccess: (entry) => router.push(`/dashboard/accounting/journal-entries/${entry.id}`),
  });

  const totals = useMemo(() => {
    const debit = lines.reduce((sum, line) => sum + amount(line.debit_amount), 0);
    const credit = lines.reduce((sum, line) => sum + amount(line.credit_amount), 0);
    return { debit, credit, difference: debit - credit };
  }, [lines]);

  const validLines = lines.filter((line) => {
    const debit = amount(line.debit_amount);
    const credit = amount(line.credit_amount);
    return line.account && ((debit > 0 && credit === 0) || (credit > 0 && debit === 0));
  });
  const isBalanced = totals.debit > 0 && totals.debit === totals.credit;
  const canSubmit = canMutate && validLines.length >= 2 && validLines.length === lines.length && isBalanced;
  const periodOptions = academicPeriods.data?.data.filter((period) => !selectedAcademicYear || period.academic_year === selectedAcademicYear) ?? [];
  const lookupError = organizations.error || branches.error || academicYears.error || academicPeriods.error || accounts.error;
  const loadingLookups = isQueryLoading(organizations, branches, academicYears, academicPeriods, accounts);

  function updateLine(id: number, field: keyof JournalLineRow, value: string) {
    setLines((current) => current.map((line) => (line.id === id ? { ...line, [field]: value } : line)));
  }

  function addLine() {
    setLines((current) => [...current, newLine(Math.max(...current.map((line) => line.id)) + 1)]);
  }

  function removeLine(id: number) {
    setLines((current) => (current.length > 2 ? current.filter((line) => line.id !== id) : current));
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!canSubmit) return;
    const formData = new FormData(event.currentTarget);
    const academicPeriod = String(formData.get("academic_period") ?? "");
    const payload: ManualJournalCreateInput = {
      organization: String(formData.get("organization") ?? ""),
      branch: String(formData.get("branch") ?? ""),
      academic_year: String(formData.get("academic_year") ?? ""),
      academic_period: academicPeriod || null,
      entry_date_ad: String(formData.get("entry_date_ad") ?? ""),
      entry_date_bs: String(formData.get("entry_date_bs") ?? ""),
      description: String(formData.get("description") ?? ""),
      narration: String(formData.get("narration") ?? ""),
      lines: lines.map((line) => ({
        account: line.account,
        description: line.description,
        debit_amount: line.debit_amount || "0.00",
        credit_amount: line.credit_amount || "0.00",
      })),
    };
    createMutation.mutate(payload);
  }

  return (
    <div className="space-y-5">
      <PageHeader
        actions={
          <Link className="rounded-md border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50" href="/dashboard/accounting/journal-entries">
            Back to journal entries
          </Link>
        }
        description="Create a balanced manual journal draft. Posting and ledger effects remain backend-controlled."
        title="New Journal Entry"
      />

      {!canMutate ? <ErrorState message="Your role can view accounting records but cannot create journal entries." title="Accounting action unavailable" /> : null}
      {loadingLookups ? <LoadingState label="Loading journal entry form..." /> : null}
      {lookupError ? <ErrorState message={lookupError instanceof Error ? lookupError.message : undefined} /> : null}
      {createMutation.isError ? (
        <ErrorState message={createMutation.error instanceof Error ? createMutation.error.message : "Unable to create journal entry."} title="Creation failed" />
      ) : null}

      <FormCard
        description="Create a draft with balanced debit and credit lines. Approval and posting remain backend-controlled."
        onSubmit={handleSubmit}
        title="Journal draft details"
      >
        <WarningPanel tone="warning" title="Manual journal control">
          Manual journals require balanced one-sided lines and supporting documentation before posting.
        </WarningPanel>
        <fieldset className="grid gap-4 md:grid-cols-2" disabled={!canMutate || createMutation.isPending}>
          <label className="block text-sm font-medium text-slate-700">
            Organization
            <select className="mt-2 w-full rounded-md border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm" name="organization" required>
              <option value="">Select organization</option>
              {organizations.data?.data.map((organization) => (
                <option key={organization.id} value={organization.id}>
                  {organization.display_name || organization.legal_name}
                </option>
              ))}
            </select>
          </label>
          <label className="block text-sm font-medium text-slate-700">
            Branch
            <select className="mt-2 w-full rounded-md border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm" name="branch" required>
              <option value="">Select branch</option>
              {branches.data?.data.map((branch) => (
                <option key={branch.id} value={branch.id}>
                  {branch.name}
                </option>
              ))}
            </select>
          </label>
          <label className="block text-sm font-medium text-slate-700">
            Academic year
            <select
              className="mt-2 w-full rounded-md border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm"
              name="academic_year"
              onChange={(event) => setSelectedAcademicYear(event.target.value)}
              required
              value={selectedAcademicYear}
            >
              <option value="">Select academic year</option>
              {academicYears.data?.data.map((year) => (
                <option key={year.id} value={year.id}>
                  {year.name}
                </option>
              ))}
            </select>
          </label>
          <label className="block text-sm font-medium text-slate-700">
            Academic period
            <select className="mt-2 w-full rounded-md border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm" name="academic_period">
              <option value="">No academic period</option>
              {periodOptions.map((period) => (
                <option key={period.id} value={period.id}>
                  {period.name}
                </option>
              ))}
            </select>
          </label>
          <TextInput label="Entry date" name="entry_date_ad" required type="date" />
          <TextInput label="Entry date BS" maxLength={10} name="entry_date_bs" placeholder="2083-01-01" />
          <TextInput label="Description" name="description" required />
        </fieldset>

        <label className="block text-sm font-medium text-slate-700">
          Narration
          <textarea className="mt-2 min-h-24 w-full rounded-md border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm" disabled={!canMutate} name="narration" />
        </label>

        <section className="space-y-3">
          <div className="flex items-center justify-between gap-3">
            <h2 className="text-base font-semibold text-[#262B40]">Journal lines</h2>
            <Button disabled={!canMutate} onClick={addLine} type="button" variant="secondary">
              Add line
            </Button>
          </div>
          <div className="space-y-3">
            {lines.map((line, index) => (
              <div className="grid gap-3 rounded-md border border-slate-200 bg-slate-50 p-3 lg:grid-cols-[1.3fr_1.2fr_0.8fr_0.8fr_auto]" key={line.id}>
                <label className="block text-sm font-medium text-slate-700">
                  Account {index + 1}
                  <select
                    className="mt-2 w-full rounded-md border border-slate-200 bg-white px-3 py-2.5 text-sm"
                    disabled={!canMutate}
                    onChange={(event) => updateLine(line.id, "account", event.target.value)}
                    required
                    value={line.account}
                  >
                    <option value="">Select account</option>
                    {accounts.data?.data.map((account) => (
                      <option key={account.id} value={account.id}>
                        {account.code} - {account.name}
                      </option>
                    ))}
                  </select>
                </label>
                <TextInput disabled={!canMutate} label={`Line description ${index + 1}`} onChange={(event) => updateLine(line.id, "description", event.target.value)} value={line.description} />
                <TextInput disabled={!canMutate || amount(line.credit_amount) > 0} label={`Debit amount ${index + 1}`} min="0" onChange={(event) => updateLine(line.id, "debit_amount", event.target.value)} step="0.01" type="number" value={line.debit_amount} />
                <TextInput disabled={!canMutate || amount(line.debit_amount) > 0} label={`Credit amount ${index + 1}`} min="0" onChange={(event) => updateLine(line.id, "credit_amount", event.target.value)} step="0.01" type="number" value={line.credit_amount} />
                <div className="flex items-end">
                  <Button disabled={!canMutate || lines.length <= 2} onClick={() => removeLine(line.id)} type="button" variant="ghost">
                    Remove
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </section>

        <div className="grid gap-3 rounded-md bg-slate-50 p-4 text-sm text-slate-700 md:grid-cols-3">
          <div>Debit total: <MoneyDisplay amount={totals.debit.toFixed(2)} /></div>
          <div>Credit total: <MoneyDisplay amount={totals.credit.toFixed(2)} /></div>
          <div>Difference: <MoneyDisplay amount={Math.abs(totals.difference).toFixed(2)} /></div>
        </div>
        {!isBalanced ? <p className="text-sm font-medium text-red-600">Debit and credit totals must balance before submission.</p> : null}
        {validLines.length < 2 || validLines.length !== lines.length ? <p className="text-sm font-medium text-red-600">At least two valid one-sided journal lines are required.</p> : null}

        <ActionBar>
          <Button disabled={!canSubmit} isLoading={createMutation.isPending} type="submit">
            Create draft journal
          </Button>
        </ActionBar>
      </FormCard>
    </div>
  );
}
