"use client";

import { FormEvent, useMemo, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/Button";
import { ErrorState } from "@/components/ui/ErrorState";
import { LoadingState } from "@/components/ui/LoadingState";
import { MoneyDisplay } from "@/components/ui/MoneyDisplay";
import { PageHeader } from "@/components/ui/PageHeader";
import { SimpleTable, type SimpleTableColumn } from "@/components/ui/SimpleTable";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { TextInput } from "@/components/ui/TextInput";
import { useAuth } from "@/hooks/useAuth";
import { listAcademicYears, listBranches, listOrganizations } from "@/lib/lookups";
import { createDraftTeacherPayment, listTeacherEarnings } from "@/lib/payroll";
import { listTeachers } from "@/lib/teachers";
import type { Role } from "@/types/auth";
import type { TeacherEarning, TeacherPaymentAllocationInput, TeacherPaymentDraftCreateInput } from "@/types/payroll";

const financialRoles: Role[] = ["super_admin", "institute_owner", "accountant"];
const paymentMethods = ["cash", "bank", "online", "cheque", "wallet", "other"];

function isQueryLoading(...states: { isLoading: boolean }[]) {
  return states.some((state) => state.isLoading);
}

export default function NewTeacherPaymentPage() {
  const router = useRouter();
  const { hasRole } = useAuth();
  const canMutate = financialRoles.some((role) => hasRole(role));
  const [selectedOrganization, setSelectedOrganization] = useState("");
  const [selectedBranch, setSelectedBranch] = useState("");
  const [selectedAcademicYear, setSelectedAcademicYear] = useState("");
  const [selectedTeacher, setSelectedTeacher] = useState("");
  const [selectedEarningId, setSelectedEarningId] = useState("");
  const [allocationAmount, setAllocationAmount] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  const organizations = useQuery({ queryKey: ["teacher-payment-form-organizations"], queryFn: listOrganizations });
  const branches = useQuery({ queryKey: ["teacher-payment-form-branches"], queryFn: listBranches });
  const academicYears = useQuery({ queryKey: ["teacher-payment-form-academic-years"], queryFn: listAcademicYears });
  const teachers = useQuery({ queryKey: ["teacher-payment-form-teachers"], queryFn: () => listTeachers() });
  const earningFilters = {
    organization: selectedOrganization,
    branch: selectedBranch,
    academic_year: selectedAcademicYear,
    teacher: selectedTeacher,
    open_only: true,
  };
  const earnings = useQuery({
    enabled: Boolean(selectedTeacher),
    queryKey: ["teacher-payment-form-open-earnings", earningFilters],
    queryFn: () => listTeacherEarnings(earningFilters),
  });

  const createMutation = useMutation({
    mutationFn: createDraftTeacherPayment,
    onSuccess: (payment) => {
      router.push(`/dashboard/payroll/payments/${payment.id}`);
    },
  });

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setErrorMessage("");
    const formData = new FormData(event.currentTarget);
    const selectedEarning = earnings.data?.data.find((earning) => earning.id === selectedEarningId);
    const allocationAmountNumber = Number(allocationAmount);
    if (!selectedEarning) {
      setErrorMessage("Select an unpaid posted teacher earning before creating the draft.");
      return;
    }
    if (!allocationAmount || allocationAmountNumber <= 0) {
      setErrorMessage("Allocation amount must be greater than zero.");
      return;
    }
    if (allocationAmountNumber > Number(selectedEarning.balance_amount)) {
      setErrorMessage("Allocation amount cannot exceed the selected earning balance.");
      return;
    }
    const allocations: TeacherPaymentAllocationInput[] =
      selectedEarningId && allocationAmount ? [{ teacher_earning: selectedEarningId, amount_allocated: allocationAmount }] : [];
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
  const selectedEarning = earnings.data?.data.find((earning) => earning.id === selectedEarningId);
  const allocationAmountNumber = Number(allocationAmount) || 0;
  const allocationValidationMessage =
    selectedEarning && allocationAmountNumber > Number(selectedEarning.balance_amount)
      ? "Allocation amount cannot exceed the selected earning balance."
      : "";
  const earningColumns = useMemo<SimpleTableColumn<TeacherEarning>[]>(
    () => [
      {
        header: "Select",
        render: (earning) => (
          <Button onClick={() => setSelectedEarningId(earning.id)} type="button" variant={earning.id === selectedEarningId ? "primary" : "secondary"}>
            {earning.id === selectedEarningId ? "Selected" : "Select"}
          </Button>
        ),
      },
      { header: "Period", render: (earning) => earning.period_label || earning.id },
      { header: "Date", render: (earning) => earning.earning_date_ad },
      { header: "Status", render: (earning) => <StatusBadge status={earning.status} /> },
      { header: "Net", render: (earning) => <MoneyDisplay amount={earning.net_amount} /> },
      { header: "Paid", render: (earning) => <MoneyDisplay amount={earning.paid_amount} /> },
      { header: "Balance", render: (earning) => <MoneyDisplay amount={earning.balance_amount} /> },
    ],
    [selectedEarningId],
  );

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
      {errorMessage ? <ErrorState message={errorMessage} title="Check allocation" /> : null}
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
            <select
              className="mt-2 w-full rounded-md border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm"
              name="organization"
              onChange={(event) => {
                setSelectedOrganization(event.target.value);
                setSelectedEarningId("");
              }}
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
              onChange={(event) => {
                setSelectedBranch(event.target.value);
                setSelectedEarningId("");
              }}
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
              onChange={(event) => {
                setSelectedAcademicYear(event.target.value);
                setSelectedEarningId("");
              }}
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
            Teacher
            <select
              className="mt-2 w-full rounded-md border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm"
              name="teacher"
              onChange={(event) => {
                setSelectedTeacher(event.target.value);
                setSelectedEarningId("");
                setAllocationAmount("");
              }}
              required
              value={selectedTeacher}
            >
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

        <fieldset className="grid gap-4 rounded-lg border border-slate-200 p-4" disabled={!canMutate || createMutation.isPending}>
          <div className="md:col-span-2">
            <h2 className="text-sm font-semibold text-[#262B40]">Posted earning allocation</h2>
            <p className="mt-1 text-sm text-slate-500">
              Select an unpaid posted or partial teacher earning. Backend validation still controls final allocation.
            </p>
          </div>
          {!selectedTeacher ? (
            <p className="rounded-md bg-slate-50 px-3 py-2 text-sm text-slate-600">Select a teacher to load open earnings.</p>
          ) : null}
          {earnings.isLoading ? <p className="text-sm text-slate-500">Loading open teacher earnings...</p> : null}
          {earnings.error ? (
            <p className="text-sm text-red-700">{earnings.error instanceof Error ? earnings.error.message : "Unable to load teacher earnings."}</p>
          ) : null}
          {selectedTeacher && !earnings.isLoading && !earnings.error && earnings.data?.data.length === 0 ? (
            <p className="rounded-md bg-slate-50 px-3 py-2 text-sm text-slate-600">No unpaid posted teacher earnings were found for this teacher.</p>
          ) : null}
          {earnings.data && earnings.data.data.length > 0 ? (
            <SimpleTable columns={earningColumns} getRowKey={(earning) => earning.id} rows={earnings.data.data} />
          ) : null}
          {selectedEarning ? (
            <div className="grid gap-3 rounded-md bg-slate-50 px-3 py-3 text-sm text-slate-700 md:grid-cols-3">
              <span>
                <span className="font-semibold">Selected balance:</span> <MoneyDisplay amount={selectedEarning.balance_amount} />
              </span>
              <span>
                <span className="font-semibold">Net:</span> <MoneyDisplay amount={selectedEarning.net_amount} />
              </span>
              <span>
                <span className="font-semibold">Paid:</span> <MoneyDisplay amount={selectedEarning.paid_amount} />
              </span>
            </div>
          ) : null}
          <TextInput
            disabled={!selectedEarning}
            label="Allocation amount"
            min="0.01"
            name="amount_allocated"
            onChange={(event) => setAllocationAmount(event.target.value)}
            required
            step="0.01"
            type="number"
            value={allocationAmount}
          />
          {allocationValidationMessage ? <p className="text-sm font-medium text-red-700">{allocationValidationMessage}</p> : null}
        </fieldset>

        <label className="block text-sm font-medium text-slate-700">
          Notes
          <textarea className="mt-2 min-h-24 w-full rounded-md border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm" disabled={!canMutate} name="notes" />
        </label>

        <div className="flex justify-end gap-2">
          <Button disabled={!canMutate || Boolean(allocationValidationMessage)} isLoading={createMutation.isPending} type="submit">
            Create draft payment
          </Button>
        </div>
      </form>
    </div>
  );
}
