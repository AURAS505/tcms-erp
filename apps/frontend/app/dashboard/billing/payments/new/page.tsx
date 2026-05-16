"use client";

import { FormEvent, useMemo, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/Button";
import { ErrorState } from "@/components/ui/ErrorState";
import { LoadingState } from "@/components/ui/LoadingState";
import { PageHeader } from "@/components/ui/PageHeader";
import { TextInput } from "@/components/ui/TextInput";
import { createDraftStudentPayment, listFeeDues, listInvoices } from "@/lib/billing";
import { listAcademicYears, listBranches, listOrganizations } from "@/lib/lookups";
import { listStudents } from "@/lib/students";
import type { StudentFeeDue, StudentInvoice, StudentPaymentAllocationInput, StudentPaymentDraftCreateInput } from "@/types/billing";

const paymentMethods = ["cash", "bank", "online", "cheque", "wallet", "other"];
const closedStatuses = new Set(["paid", "cancelled", "written_off"]);

type AllocationOption =
  | { kind: "due"; id: string; label: string; balance: number; status: string; source: StudentFeeDue }
  | { kind: "invoice"; id: string; label: string; balance: number; status: string; source: StudentInvoice };

function isQueryLoading(...states: { isLoading: boolean }[]) {
  return states.some((state) => state.isLoading);
}

export default function NewPaymentPage() {
  const router = useRouter();
  const [isAdvancePayment, setIsAdvancePayment] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [selectedOrganization, setSelectedOrganization] = useState("");
  const [selectedBranch, setSelectedBranch] = useState("");
  const [selectedAcademicYear, setSelectedAcademicYear] = useState("");
  const [selectedStudent, setSelectedStudent] = useState("");
  const [selectedAllocationTarget, setSelectedAllocationTarget] = useState("");
  const [allocationAmount, setAllocationAmount] = useState("");
  const [allocationSearch, setAllocationSearch] = useState("");

  const organizations = useQuery({ queryKey: ["payment-form-organizations"], queryFn: listOrganizations });
  const branches = useQuery({ queryKey: ["payment-form-branches"], queryFn: listBranches });
  const academicYears = useQuery({ queryKey: ["payment-form-academic-years"], queryFn: listAcademicYears });
  const students = useQuery({ queryKey: ["payment-form-students"], queryFn: () => listStudents() });
  const allocationFilters = {
    organization: selectedOrganization,
    branch: selectedBranch,
    academic_year: selectedAcademicYear,
  };
  const allocationEnabled = Boolean(selectedStudent) && !isAdvancePayment;
  const feeDues = useQuery({
    enabled: allocationEnabled,
    queryKey: ["payment-form-fee-dues", allocationFilters],
    queryFn: () => listFeeDues(allocationFilters),
  });
  const invoices = useQuery({
    enabled: allocationEnabled,
    queryKey: ["payment-form-invoices", allocationFilters],
    queryFn: () => listInvoices(allocationFilters),
  });

  const createMutation = useMutation({
    mutationFn: createDraftStudentPayment,
    onSuccess: (payment) => {
      router.push(`/dashboard/billing/payments/${payment.id}`);
    },
  });

  const allAllocationOptions = useMemo<AllocationOption[]>(() => {
    const dueOptions =
      feeDues.data?.data
        .filter((due) => due.student === selectedStudent && Number(due.balance_amount) > 0 && !closedStatuses.has(due.status))
        .map<AllocationOption>((due) => ({
          kind: "due",
          id: due.id,
          label: `Due: ${due.period_label || due.id}`,
          balance: Number(due.balance_amount),
          status: due.status,
          source: due,
        })) ?? [];
    const invoiceOptions =
      invoices.data?.data
        .filter((invoice) => invoice.student === selectedStudent && Number(invoice.balance_amount) > 0 && !closedStatuses.has(invoice.status))
        .map<AllocationOption>((invoice) => ({
          kind: "invoice",
          id: invoice.id,
          label: `Invoice: ${invoice.invoice_number || invoice.id}`,
          balance: Number(invoice.balance_amount),
          status: invoice.status,
          source: invoice,
        })) ?? [];
    return [...dueOptions, ...invoiceOptions];
  }, [feeDues.data?.data, invoices.data?.data, selectedStudent]);

  const allocationOptions = useMemo(() => {
    const normalizedSearch = allocationSearch.trim().toLowerCase();
    if (!normalizedSearch) return allAllocationOptions;
    return allAllocationOptions.filter((option) => `${option.label} ${option.status}`.toLowerCase().includes(normalizedSearch));
  }, [allAllocationOptions, allocationSearch]);

  const selectedAllocation = allAllocationOptions.find((option) => `${option.kind}:${option.id}` === selectedAllocationTarget);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setErrorMessage("");
    const formData = new FormData(event.currentTarget);
    const amount = String(formData.get("amount") ?? "").trim();

    const allocations: StudentPaymentAllocationInput[] = [];
    if (!isAdvancePayment && selectedAllocationTarget) {
      const parsedAllocationAmount = Number(allocationAmount);
      if (!allocationAmount || parsedAllocationAmount <= 0) {
        setErrorMessage("Allocation amount must be greater than zero.");
        return;
      }
      if (!selectedAllocation) {
        setErrorMessage("Select a valid due or invoice allocation target.");
        return;
      }
      if (parsedAllocationAmount > selectedAllocation.balance) {
        setErrorMessage("Allocation amount cannot exceed the selected balance.");
        return;
      }
      allocations.push(
        selectedAllocation.kind === "due"
          ? { fee_due: selectedAllocation.id, amount_allocated: allocationAmount }
          : { invoice: selectedAllocation.id, amount_allocated: allocationAmount },
      );
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
      allocations,
    };

    createMutation.mutate(payload);
  }

  const loadingLookups = isQueryLoading(organizations, branches, academicYears, students);
  const lookupError = organizations.error || branches.error || academicYears.error || students.error;
  const loadingAllocations = feeDues.isLoading || invoices.isLoading;
  const allocationError = feeDues.error || invoices.error;

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
            <select
              className="mt-2 w-full rounded-md border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm"
              name="organization"
              onChange={(event) => setSelectedOrganization(event.target.value)}
              required
              value={selectedOrganization}
            >
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
            <select
              className="mt-2 w-full rounded-md border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm"
              name="branch"
              onChange={(event) => setSelectedBranch(event.target.value)}
              required
              value={selectedBranch}
            >
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
            Student
            <select
              className="mt-2 w-full rounded-md border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm"
              name="student"
              onChange={(event) => {
                setSelectedStudent(event.target.value);
                setSelectedAllocationTarget("");
                setAllocationAmount("");
                setAllocationSearch("");
              }}
              required
              value={selectedStudent}
            >
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
          <input
            checked={isAdvancePayment}
            className="h-4 w-4 rounded border-slate-300"
            onChange={(event) => {
              setIsAdvancePayment(event.target.checked);
              if (event.target.checked) {
                setSelectedAllocationTarget("");
                setAllocationAmount("");
                setAllocationSearch("");
              }
            }}
            type="checkbox"
          />
          Advance payment
        </label>

        <div className="rounded-lg border border-slate-200 p-4">
          <h2 className="text-sm font-semibold text-[#262B40]">Optional due or invoice allocation</h2>
          <p className="mt-1 text-sm text-slate-500">Select an open due or invoice for this student. Backend validation still controls final allocation.</p>
          {isAdvancePayment ? (
            <p className="mt-4 rounded-md bg-slate-50 px-3 py-2 text-sm text-slate-600">Advance payments do not use due or invoice allocations.</p>
          ) : (
            <div className="mt-4 grid gap-4 md:grid-cols-2">
              <TextInput
                disabled={!selectedStudent || loadingAllocations}
                label="Search dues/invoices"
                name="allocation_search"
                onChange={(event) => setAllocationSearch(event.target.value)}
                value={allocationSearch}
              />
              <label className="block text-sm font-medium text-slate-700">
                Allocation target
                <select
                  className="mt-2 w-full rounded-md border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm disabled:cursor-not-allowed disabled:opacity-60"
                  disabled={!selectedStudent || loadingAllocations}
                  name="allocation_target"
                  onChange={(event) => {
                    setSelectedAllocationTarget(event.target.value);
                    setAllocationAmount("");
                  }}
                  value={selectedAllocationTarget}
                >
                  <option value="">{selectedStudent ? "Select due or invoice" : "Select student first"}</option>
                  {allocationOptions.map((option) => (
                    <option key={`${option.kind}:${option.id}`} value={`${option.kind}:${option.id}`}>
                      {option.label} - balance {option.balance.toFixed(2)}
                    </option>
                  ))}
                </select>
              </label>
              <TextInput
                disabled={!selectedAllocation}
                label="Allocation amount"
                min="0.01"
                name="allocation_amount"
                onChange={(event) => setAllocationAmount(event.target.value)}
                step="0.01"
                type="number"
                value={allocationAmount}
              />
              {loadingAllocations ? <p className="text-sm text-slate-500 md:col-span-2">Loading open dues and invoices...</p> : null}
              {allocationError ? (
                <p className="text-sm text-red-700 md:col-span-2">{allocationError instanceof Error ? allocationError.message : "Unable to load allocation targets."}</p>
              ) : null}
              {selectedStudent && !loadingAllocations && !allocationError && allocationOptions.length === 0 ? (
                <p className="text-sm text-slate-500 md:col-span-2">No open dues or invoices were found for this student in the loaded results.</p>
              ) : null}
              {selectedAllocation ? (
                <div className="rounded-md bg-slate-50 px-3 py-2 text-sm text-slate-600 md:col-span-2">
                  <span className="font-semibold text-slate-700">Selected balance:</span> {selectedAllocation.balance.toFixed(2)}
                  <span className="mx-2 text-slate-300">|</span>
                  <span className="font-semibold text-slate-700">Status:</span> {selectedAllocation.status}
                </div>
              ) : null}
            </div>
          )}
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
