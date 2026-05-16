"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/Button";
import { ErrorState } from "@/components/ui/ErrorState";
import { LoadingState } from "@/components/ui/LoadingState";
import { PageHeader } from "@/components/ui/PageHeader";
import { TextInput } from "@/components/ui/TextInput";
import { useAuth } from "@/hooks/useAuth";
import { listAcademicPeriods, listAcademicYears, listBranches, listOrganizations } from "@/lib/lookups";
import { createManualTeacherEarning } from "@/lib/payroll";
import { listTeachers } from "@/lib/teachers";
import type { Role } from "@/types/auth";
import type { TeacherEarningCreateInput } from "@/types/payroll";

const financialRoles: Role[] = ["super_admin", "institute_owner", "accountant"];

function isQueryLoading(...states: { isLoading: boolean }[]) {
  return states.some((state) => state.isLoading);
}

export default function NewTeacherEarningPage() {
  const router = useRouter();
  const { hasRole } = useAuth();
  const canMutate = financialRoles.some((role) => hasRole(role));
  const [selectedAcademicYear, setSelectedAcademicYear] = useState("");

  const organizations = useQuery({ queryKey: ["teacher-earning-form-organizations"], queryFn: listOrganizations });
  const branches = useQuery({ queryKey: ["teacher-earning-form-branches"], queryFn: listBranches });
  const academicYears = useQuery({ queryKey: ["teacher-earning-form-academic-years"], queryFn: listAcademicYears });
  const academicPeriods = useQuery({ queryKey: ["teacher-earning-form-academic-periods"], queryFn: listAcademicPeriods });
  const teachers = useQuery({ queryKey: ["teacher-earning-form-teachers"], queryFn: () => listTeachers() });

  const createMutation = useMutation({
    mutationFn: createManualTeacherEarning,
    onSuccess: (earning) => {
      router.push(`/dashboard/payroll/earnings/${earning.id}`);
    },
  });

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const academicPeriod = String(formData.get("academic_period") ?? "");
    const deductionAmount = String(formData.get("deduction_amount") ?? "").trim();
    const payload: TeacherEarningCreateInput = {
      organization: String(formData.get("organization") ?? ""),
      branch: String(formData.get("branch") ?? ""),
      academic_year: String(formData.get("academic_year") ?? ""),
      academic_period: academicPeriod || null,
      teacher: String(formData.get("teacher") ?? ""),
      earning_date_ad: String(formData.get("earning_date_ad") ?? ""),
      gross_amount: String(formData.get("gross_amount") ?? ""),
      deduction_amount: deductionAmount || "0.00",
      notes: String(formData.get("notes") ?? ""),
    };
    createMutation.mutate(payload);
  }

  const loadingLookups = isQueryLoading(organizations, branches, academicYears, academicPeriods, teachers);
  const lookupError = organizations.error || branches.error || academicYears.error || academicPeriods.error || teachers.error;
  const periodOptions = academicPeriods.data?.data.filter((period) => !selectedAcademicYear || period.academic_year === selectedAcademicYear) ?? [];

  return (
    <div className="space-y-5">
      <PageHeader
        actions={
          <Link className="rounded-md border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50" href="/dashboard/payroll/earnings">
            Back to earnings
          </Link>
        }
        description="Create a manual teacher earning. Accounting effects are handled only when the backend posts the earning."
        title="New Teacher Earning"
      />

      {!canMutate ? (
        <ErrorState message="Your role can view payroll records but cannot create teacher earnings." title="Payroll action unavailable" />
      ) : null}
      {loadingLookups ? <LoadingState label="Loading teacher earning form..." /> : null}
      {lookupError ? <ErrorState message={lookupError instanceof Error ? lookupError.message : undefined} /> : null}
      {createMutation.isError ? (
        <ErrorState
          message={createMutation.error instanceof Error ? createMutation.error.message : "Unable to create teacher earning."}
          title="Creation failed"
        />
      ) : null}

      <form className="grid gap-5 rounded-lg bg-white p-5 shadow-[0_2px_18px_rgba(38,43,64,0.08)]" onSubmit={handleSubmit}>
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
          <label className="block text-sm font-medium text-slate-700">
            Teacher
            <select className="mt-2 w-full rounded-md border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm" name="teacher" required>
              <option value="">Select teacher</option>
              {teachers.data?.data.map((teacher) => (
                <option key={teacher.id} value={teacher.id}>
                  {teacher.full_name}
                </option>
              ))}
            </select>
          </label>
          <TextInput label="Earning date" name="earning_date_ad" required type="date" />
          <TextInput label="Gross amount" min="0.01" name="gross_amount" required step="0.01" type="number" />
          <TextInput label="Deduction amount" min="0" name="deduction_amount" step="0.01" type="number" />
        </fieldset>

        <label className="block text-sm font-medium text-slate-700">
          Notes
          <textarea className="mt-2 min-h-24 w-full rounded-md border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm" disabled={!canMutate} name="notes" />
        </label>

        <div className="flex justify-end gap-2">
          <Button disabled={!canMutate} isLoading={createMutation.isPending} type="submit">
            Create manual earning
          </Button>
        </div>
      </form>
    </div>
  );
}
