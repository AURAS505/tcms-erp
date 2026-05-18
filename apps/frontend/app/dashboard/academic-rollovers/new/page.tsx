"use client";

import { FormEvent } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/Button";
import { ErrorState } from "@/components/ui/ErrorState";
import { ActionBar } from "@/components/ui/ActionBar";
import { FormCard } from "@/components/ui/FormCard";
import { LoadingState } from "@/components/ui/LoadingState";
import { PageHeader } from "@/components/ui/PageHeader";
import { WarningPanel } from "@/components/ui/WarningPanel";
import { useAuth } from "@/hooks/useAuth";
import { listAcademicYears, prepareAcademicRollover } from "@/lib/academic";
import { listOrganizations } from "@/lib/lookups";
import type { Role } from "@/types/auth";

const rolloverRoles: Role[] = ["super_admin", "institute_owner", "accountant"];

export default function NewAcademicRolloverPage() {
  const router = useRouter();
  const { hasRole } = useAuth();
  const canMutate = rolloverRoles.some((role) => hasRole(role));
  const organizations = useQuery({ queryKey: ["rollover-form-organizations"], queryFn: listOrganizations });
  const years = useQuery({ queryKey: ["rollover-form-academic-years"], queryFn: () => listAcademicYears() });
  const prepare = useMutation({
    mutationFn: prepareAcademicRollover,
    onSuccess: (rollover) => router.push(`/dashboard/academic-rollovers/${rollover.id}`),
  });

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!canMutate) return;
    const formData = new FormData(event.currentTarget);
    prepare.mutate({
      organization: String(formData.get("organization") ?? ""),
      from_academic_year: String(formData.get("from_academic_year") ?? ""),
      notes: String(formData.get("notes") ?? ""),
    });
  }

  return (
    <div className="space-y-5">
      <PageHeader
        actions={
          <Link className="rounded-md border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50" href="/dashboard/academic-rollovers">
            Back to rollovers
          </Link>
        }
        description="Prepare a rollover record. Target year details are supplied during execution after validation."
        title="New Academic Rollover"
      />
      {!canMutate ? <ErrorState message="Your role can view rollovers but cannot prepare them." title="Rollover action unavailable" /> : null}
      {organizations.isLoading || years.isLoading ? <LoadingState label="Loading rollover form..." /> : null}
      {organizations.error || years.error ? <ErrorState message="Unable to load rollover form options." /> : null}
      {prepare.isError ? <ErrorState message={prepare.error instanceof Error ? prepare.error.message : undefined} title="Prepare failed" /> : null}
      <FormCard
        description="Prepare the rollover record first. Validation, closing entries, opening balances, and activation remain backend-controlled."
        onSubmit={handleSubmit}
        title="Rollover preparation"
      >
        <fieldset className="grid gap-4 md:grid-cols-2" disabled={!canMutate || prepare.isPending}>
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
            Outgoing academic year
            <select className="mt-2 w-full rounded-md border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm" name="from_academic_year" required>
              <option value="">Select outgoing year</option>
              {years.data?.data.map((year) => (
                <option key={year.id} value={year.id}>
                  {year.name} ({year.status})
                </option>
              ))}
            </select>
          </label>
        </fieldset>
        <label className="block text-sm font-medium text-slate-700">
          Notes
          <textarea className="mt-2 min-h-24 w-full rounded-md border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm" disabled={!canMutate} name="notes" />
        </label>
        <WarningPanel tone="danger" title="High-risk financial workflow">
          Rollover is a high-risk financial process. Validation and execution remain backend-controlled.
        </WarningPanel>
        <ActionBar>
          <Button disabled={!canMutate} isLoading={prepare.isPending} type="submit">Prepare rollover</Button>
        </ActionBar>
      </FormCard>
    </div>
  );
}
