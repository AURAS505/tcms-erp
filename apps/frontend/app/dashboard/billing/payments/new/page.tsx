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
import { createDraftStudentPayment } from "@/lib/billing";
import { listAcademicYears, listBranches, listOrganizations } from "@/lib/lookups";
import { listStudents } from "@/lib/students";
import type { StudentPaymentDraftCreateInput } from "@/types/billing";

const paymentMethods = ["cash", "bank", "online", "cheque", "wallet", "other"];

function isQueryLoading(...states: { isLoading: boolean }[]) {
  return states.some((state) => state.isLoading);
}

export default function NewPaymentPage() {
  const router = useRouter();
  const [isAdvancePayment, setIsAdvancePayment] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const organizations = useQuery({ queryKey: ["payment-form-organizations"], queryFn: listOrganizations });
  const branches = useQuery({ queryKey: ["payment-form-branches"], queryFn: listBranches });
  const academicYears = useQuery({ queryKey: ["payment-form-academic-years"], queryFn: listAcademicYears });
  const students = useQuery({ queryKey: ["payment-form-students"], queryFn: () => listStudents() });

  const createMutation = useMutation({
    mutationFn: createDraftStudentPayment,
    onSuccess: (payment) => {
      router.push(`/dashboard/billing/payments/${payment.id}`);
    },
  });

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setErrorMessage("");
    const formData = new FormData(event.currentTarget);
    const allocationDue = String(formData.get("allocation_fee_due") ?? "").trim();
    const allocationAmount = String(formData.get("allocation_amount") ?? "").trim();
    const amount = String(formData.get("amount") ?? "").trim();

    if (!isAdvancePayment && allocationDue && !allocationAmount) {
      setErrorMessage("Allocation amount is required when a due ID is provided.");
      return;
    }

    const payload: StudentPaymentDraftCreateInput = {
      organization: String(formData.get("organization") ?? ""),
      branch: String(formData.get("branch") ?? ""),
      academic_year: String(formData.get("academic_year") ?? ""),
      student: String(formData.get("student") ?? ""),
      payment_date_ad: String(formData.get("payment_date_ad") ?? ""),
      payment_method: String(formData.get("payment_method") ?? "cash"),
      amount,
      is_advance_payment: isAdvancePayment,
      reference_number: String(formData.get("reference_number") ?? ""),
      notes: String(formData.get("notes") ?? ""),
      allocations:
        !isAdvancePayment && allocationDue
          ? [{ fee_due: allocationDue, amount_allocated: allocationAmount || amount }]
          : [],
    };

    createMutation.mutate(payload);
  }

  const loadingLookups = isQueryLoading(organizations, branches, academicYears, students);
  const lookupError = organizations.error || branches.error || academicYears.error || students.error;

  return (
    <div className="space-y-5">
      <PageHeader
        actions={
          <Link className="rounded-md border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50" href="/dashboard/billing/payments">
            Back to payments
          </Link>
        }
        description="Create a draft student payment. Posting and accounting effects are handled only by backend approval."
        title="New Payment"
      />

      {loadingLookups ? <LoadingState label="Loading payment form..." /> : null}
      {lookupError ? <ErrorState message={lookupError instanceof Error ? lookupError.message : undefined} /> : null}
      {errorMessage ? <ErrorState message={errorMessage} title="Check payment details" /> : null}
      {createMutation.isError ? (
        <ErrorState
          message={createMutation.error instanceof Error ? createMutation.error.message : "Unable to create draft payment."}
          title="Draft creation failed"
        />
      ) : null}

      <form className="grid gap-5 rounded-lg bg-white p-5 shadow-[0_2px_18px_rgba(38,43,64,0.08)]" onSubmit={handleSubmit}>
        <div className="grid gap-4 md:grid-cols-2">
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
            Student
            <select className="mt-2 w-full rounded-md border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm" name="student" required>
              <option value="">Select student</option>
              {students.data?.data.map((student) => (
                <option key={student.id} value={student.id}>
                  {student.full_name}
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
        </div>

        <label className="flex items-center gap-3 text-sm font-medium text-slate-700">
          <input checked={isAdvancePayment} className="h-4 w-4 rounded border-slate-300" onChange={(event) => setIsAdvancePayment(event.target.checked)} type="checkbox" />
          Advance payment
        </label>

        <div className="rounded-lg border border-slate-200 p-4">
          <h2 className="text-sm font-semibold text-[#262B40]">Optional due allocation</h2>
          <p className="mt-1 text-sm text-slate-500">Enter a due ID only when allocating this draft to an existing due.</p>
          <div className="mt-4 grid gap-4 md:grid-cols-2">
            <TextInput disabled={isAdvancePayment} label="Due ID" name="allocation_fee_due" />
            <TextInput disabled={isAdvancePayment} label="Allocation amount" min="0.01" name="allocation_amount" step="0.01" type="number" />
          </div>
        </div>

        <label className="block text-sm font-medium text-slate-700">
          Notes
          <textarea className="mt-2 min-h-24 w-full rounded-md border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm" name="notes" />
        </label>

        <div className="flex justify-end gap-2">
          <Button isLoading={createMutation.isPending} type="submit">
            Create draft
          </Button>
        </div>
      </form>
    </div>
  );
}
