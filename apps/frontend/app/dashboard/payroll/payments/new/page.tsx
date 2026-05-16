"use client";

import { FormEvent } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/Button";
import { ErrorState } from "@/components/ui/ErrorState";
import { LoadingState } from "@/components/ui/LoadingState";
import { PageHeader } from "@/components/ui/PageHeader";
import { TextInput } from "@/components/ui/TextInput";
import { useAuth } from "@/hooks/useAuth";
import { listAcademicYears, listBranches, listOrganizations } from "@/lib/lookups";
import { createDraftTeacherPayment } from "@/lib/payroll";
import { listTeachers } from "@/lib/teachers";
import type { Role } from "@/types/auth";
import type { TeacherPaymentAllocationInput, TeacherPaymentDraftCreateInput } from "@/types/payroll";

const financialRoles: Role[] = ["super_admin", "institute_owner", "accountant"];
const paymentMethods = ["cash", "bank", "online", "cheque", "wallet", "other"];

function isQueryLoading(...states: { isLoading: boolean }[]) {
  return states.some((state) => state.isLoading);
}

export default function NewTeacherPaymentPage() {
  const router = useRouter();
  const { hasRole } = useAuth();
  const canMutate = financialRoles.some((role) => hasRole(role));

  const organizations = useQuery({ queryKey: ["teacher-payment-form-organizations"], queryFn: listOrganizations });
  const branches = useQuery({ queryKey: ["teacher-payment-form-branches"], queryFn: listBranches });
  const academicYears = useQuery({ queryKey: ["teacher-payment-form-academic-years"], queryFn: listAcademicYears });
  const teachers = useQuery({ queryKey: ["teacher-payment-form-teachers"], queryFn: () => listTeachers() });

  const createMutation = useMutation({
    mutationFn: createDraftTeacherPayment,
    onSuccess: (payment) => {
      router.push(`/dashboard/payroll/payments/${payment.id}`);
    },
  });

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const earningId = String(formData.get("teacher_earning") ?? "").trim();
    const allocationAmount = String(formData.get("amount_allocated") ?? "").trim();
    const allocations: TeacherPaymentAllocationInput[] =
      earningId && allocationAmount ? [{ teacher_earning: earningId, amount_allocated: allocationAmount }] : [];
    const payload: TeacherPaymentDraftCreateInput = {
      organization: String(formData.get("organization") ?? ""),
      branch: String(formData.get("branch") ?? ""),
      academic_year: String(formData.get("academic_year") ?? ""),
      teacher: String(formData.get("teacher") ?? ""),
      payment_date_ad: String(formData.get("payment_date_ad") ?? ""),
      payment_method: String(formData.get("payment_method") ?? "cash"),
      amount: String(formData.get("amount") ?? ""),
      reference_number: String(formData.get("reference_number") ?? ""),
      notes: String(formData.get("notes") ?? ""),
      allocations,
    };
    createMutation.mutate(payload);
  }

  const loadingLookups = isQueryLoading(organizations, branches, academicYears, teachers);
  const lookupError = organizations.error || branches.error || academicYears.error || teachers.error;

  return (
    <div className="space-y-5">
      <PageHeader
        actions={
          <Link className="rounded-md border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50" href="/dashboard/payroll/payments">
            Back to teacher payments
          </Link>
        }
        description="Create a draft teacher payment. Allocation and posting validation remain backend-controlled."
        title="New Teacher Payment"
      />

      {!canMutate ? (
        <ErrorState message="Your role can view payroll records but cannot create teacher payments." title="Payroll action unavailable" />
      ) : null}
      {loadingLookups ? <LoadingState label="Loading teacher payment form..." /> : null}
      {lookupError ? <ErrorState message={lookupError instanceof Error ? lookupError.message : undefined} /> : null}
      {createMutation.isError ? (
        <ErrorState
          message={createMutation.error instanceof Error ? createMutation.error.message : "Unable to create teacher payment."}
          title="Draft creation failed"
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
            <select className="mt-2 w-full rounded-md border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm" name="academic_year" required>
              <option value="">Select academic year</option>
              {academicYears.data?.data.map((year) => (
                <option key={year.id} value={year.id}>
                  {year.name}
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
          <TextInput label="Payment date" name="payment_date_ad" required type="date" />
          <label className="block text-sm font-medium text-slate-700">
            Payment method
            <select className="mt-2 w-full rounded-md border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm" name="payment_method" required>
              {paymentMethods.map((method) => (
                <option key={method} value={method}>
                  {method.charAt(0).toUpperCase() + method.slice(1)}
                </option>
              ))}
            </select>
          </label>
          <TextInput label="Amount" min="0.01" name="amount" required step="0.01" type="number" />
          <TextInput label="Reference number" name="reference_number" />
        </fieldset>

        <fieldset className="grid gap-4 rounded-lg border border-slate-200 p-4 md:grid-cols-2" disabled={!canMutate || createMutation.isPending}>
          <div className="md:col-span-2">
            <h2 className="text-sm font-semibold text-[#262B40]">Manual earning allocation</h2>
            <p className="mt-1 text-sm text-slate-500">
              Enter the posted teacher earning ID and allocation amount. The backend validates branch, teacher, status, and balance.
            </p>
          </div>
          <TextInput label="Teacher earning ID" name="teacher_earning" required />
          <TextInput label="Allocation amount" min="0.01" name="amount_allocated" required step="0.01" type="number" />
        </fieldset>

        <label className="block text-sm font-medium text-slate-700">
          Notes
          <textarea className="mt-2 min-h-24 w-full rounded-md border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm" disabled={!canMutate} name="notes" />
        </label>

        <div className="flex justify-end gap-2">
          <Button disabled={!canMutate} isLoading={createMutation.isPending} type="submit">
            Create draft payment
          </Button>
        </div>
      </form>
    </div>
  );
}
