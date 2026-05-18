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
import { SimpleTable, type SimpleTableColumn } from "@/components/ui/SimpleTable";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { TextInput } from "@/components/ui/TextInput";
import { WarningPanel } from "@/components/ui/WarningPanel";
import { useAuth } from "@/hooks/useAuth";
import { listAcademicYears, listBranches, listOrganizations } from "@/lib/lookups";
import { createDraftTeacherPayment, listTeacherEarnings } from "@/lib/payroll";
import { listTeachers } from "@/lib/teachers";
import type { Role } from "@/types/auth";
import type { TeacherEarning, TeacherPaymentAllocationInput, TeacherPaymentDraftCreateInput } from "@/types/payroll";

const financialRoles: Role[] = ["super_admin", "institute_owner", "accountant"];
const paymentMethods = ["cash", "bank", "online", "cheque", "wallet", "other"];

interface AllocationRow {
  id: string;
  earningId: string;
  amount: string;
}

function newAllocationRow(): AllocationRow {
  return { id: `${Date.now()}-${Math.random()}`, earningId: "", amount: "" };
}

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
  const [paymentAmount, setPaymentAmount] = useState("");
  const [allocationRows, setAllocationRows] = useState<AllocationRow[]>([newAllocationRow()]);
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

  const openEarnings = earnings.data?.data ?? [];
  const selectedTargets = allocationRows.map((row) => row.earningId).filter(Boolean);
  const duplicateTargets = new Set(selectedTargets.filter((target, index) => selectedTargets.indexOf(target) !== index));
  const paymentAmountNumber = Number(paymentAmount) || 0;
  const allocationTotal = allocationRows.reduce((total, row) => total + (Number(row.amount) || 0), 0);
  const unallocatedAmount = paymentAmountNumber - allocationTotal;
  const allocationValidationMessages = allocationRows.flatMap((row, index) => {
    const messages: string[] = [];
    const selectedEarning = openEarnings.find((earning) => earning.id === row.earningId);
    const parsedAmount = Number(row.amount);
    if (!row.earningId) messages.push(`Allocation row ${index + 1} needs an earning.`);
    if (!row.amount || parsedAmount <= 0) messages.push(`Allocation row ${index + 1} amount must be greater than zero.`);
    if (row.earningId && duplicateTargets.has(row.earningId)) messages.push(`Allocation row ${index + 1} duplicates another allocation.`);
    if (selectedEarning && parsedAmount > Number(selectedEarning.balance_amount)) {
      messages.push(`Allocation row ${index + 1} amount cannot exceed the selected earning balance.`);
    }
    return messages;
  });
  if (allocationTotal > paymentAmountNumber) {
    allocationValidationMessages.push("Allocation total cannot exceed payment amount.");
  }
  const hasAllocationValidationError =
    paymentAmountNumber <= 0 || allocationRows.length === 0 || allocationValidationMessages.length > 0;

  function resetAllocations() {
    setAllocationRows([newAllocationRow()]);
    setErrorMessage("");
  }

  function updateAllocationRow(rowId: string, patch: Partial<AllocationRow>) {
    setAllocationRows((rows) => rows.map((row) => (row.id === rowId ? { ...row, ...patch } : row)));
  }

  function removeAllocationRow(rowId: string) {
    setAllocationRows((rows) => {
      const nextRows = rows.filter((row) => row.id !== rowId);
      return nextRows.length ? nextRows : [newAllocationRow()];
    });
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setErrorMessage("");
    if (hasAllocationValidationError) {
      setErrorMessage(allocationValidationMessages[0] || "Payment amount and allocation rows are required.");
      return;
    }
    const formData = new FormData(event.currentTarget);
    const allocations: TeacherPaymentAllocationInput[] = allocationRows.map((row) => ({
      teacher_earning: row.earningId,
      amount_allocated: row.amount,
    }));
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
  const earningColumns = useMemo<SimpleTableColumn<TeacherEarning>[]>(
    () => [
      { header: "Period", render: (earning) => earning.period_label || earning.id },
      { header: "Date", render: (earning) => earning.earning_date_ad },
      { header: "Status", render: (earning) => <StatusBadge status={earning.status} /> },
      { header: "Net", render: (earning) => <MoneyDisplay amount={earning.net_amount} /> },
      { header: "Paid", render: (earning) => <MoneyDisplay amount={earning.paid_amount} /> },
      { header: "Balance", render: (earning) => <MoneyDisplay amount={earning.balance_amount} /> },
    ],
    [],
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

      <FormCard
        description="Capture payment allocation against approved teacher earnings. Posting remains backend-controlled."
        onSubmit={handleSubmit}
        title="Teacher payment draft details"
      >
        <WarningPanel tone="info" title="Payroll ledger boundary">
          Draft teacher payments do not affect cash or teacher payable accounts until backend approval and posting succeeds.
        </WarningPanel>
        <fieldset className="grid gap-4 md:grid-cols-2" disabled={!canMutate || createMutation.isPending}>
          <label className="block text-sm font-medium text-slate-700">
            Organization
            <select
              className="mt-2 w-full rounded-md border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm"
              name="organization"
              onChange={(event) => {
                setSelectedOrganization(event.target.value);
                resetAllocations();
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
                resetAllocations();
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
                resetAllocations();
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
                resetAllocations();
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
          <TextInput label="Amount" min="0.01" name="amount" onChange={(event) => setPaymentAmount(event.target.value)} required step="0.01" type="number" value={paymentAmount} />
          <TextInput label="Reference number" name="reference_number" />
        </fieldset>

        <fieldset className="grid gap-4 rounded-lg border border-slate-200 p-4" disabled={!canMutate || createMutation.isPending}>
          <div>
            <h2 className="text-sm font-semibold text-[#262B40]">Posted earning allocations</h2>
            <p className="mt-1 text-sm text-slate-500">
              Select one or more unpaid posted or partial teacher earnings. Backend validation still controls final allocation.
            </p>
          </div>
          {!selectedTeacher ? (
            <p className="rounded-md bg-slate-50 px-3 py-2 text-sm text-slate-600">Select a teacher to load open earnings.</p>
          ) : null}
          {earnings.isLoading ? <p className="text-sm text-slate-500">Loading open teacher earnings...</p> : null}
          {earnings.error ? (
            <p className="text-sm text-red-700">{earnings.error instanceof Error ? earnings.error.message : "Unable to load teacher earnings."}</p>
          ) : null}
          {selectedTeacher && !earnings.isLoading && !earnings.error && openEarnings.length === 0 ? (
            <p className="rounded-md bg-slate-50 px-3 py-2 text-sm text-slate-600">No unpaid posted teacher earnings were found for this teacher.</p>
          ) : null}
          {openEarnings.length > 0 ? <SimpleTable columns={earningColumns} getRowKey={(earning) => earning.id} rows={openEarnings} /> : null}

          <div className="space-y-3">
            {allocationRows.map((row, index) => {
              const selectedEarning = openEarnings.find((earning) => earning.id === row.earningId);
              return (
                <div className="grid gap-3 rounded-md border border-slate-200 p-3 md:grid-cols-[1fr_180px_auto]" key={row.id}>
                  <label className="block text-sm font-medium text-slate-700">
                    Earning {index + 1}
                    <select
                      className="mt-2 w-full rounded-md border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm disabled:cursor-not-allowed disabled:opacity-60"
                      disabled={!selectedTeacher || earnings.isLoading || openEarnings.length === 0}
                      name={`teacher_earning_${index + 1}`}
                      onChange={(event) => updateAllocationRow(row.id, { earningId: event.target.value, amount: "" })}
                      value={row.earningId}
                    >
                      <option value="">{selectedTeacher ? "Select earning" : "Select teacher first"}</option>
                      {openEarnings.map((earning) => {
                        const disabled = Boolean(earning.id !== row.earningId && selectedTargets.includes(earning.id));
                        return (
                          <option disabled={disabled} key={earning.id} value={earning.id}>
                            {earning.period_label || earning.id} - {earning.earning_date_ad} - balance {Number(earning.balance_amount).toFixed(2)}
                          </option>
                        );
                      })}
                    </select>
                  </label>
                  <TextInput
                    disabled={!selectedEarning}
                    label={`Allocation amount ${index + 1}`}
                    min="0.01"
                    name={`amount_allocated_${index + 1}`}
                    onChange={(event) => updateAllocationRow(row.id, { amount: event.target.value })}
                    step="0.01"
                    type="number"
                    value={row.amount}
                  />
                  <div className="flex items-end">
                    <Button disabled={allocationRows.length === 1 && !row.earningId && !row.amount} onClick={() => removeAllocationRow(row.id)} type="button" variant="secondary">
                      Remove
                    </Button>
                  </div>
                  {selectedEarning ? (
                    <div className="grid gap-2 rounded-md bg-slate-50 px-3 py-2 text-sm text-slate-700 md:col-span-3 md:grid-cols-3">
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
                </div>
              );
            })}
          </div>

          <Button disabled={!selectedTeacher || earnings.isLoading || openEarnings.length === 0} onClick={() => setAllocationRows((rows) => [...rows, newAllocationRow()])} type="button" variant="secondary">
            Add allocation
          </Button>

          <div className="grid gap-2 rounded-md bg-slate-50 px-3 py-3 text-sm text-slate-700 md:grid-cols-3">
            <span>
              <span className="font-semibold">Payment amount:</span> <MoneyDisplay amount={paymentAmountNumber} />
            </span>
            <span>
              <span className="font-semibold">Allocation total:</span> <MoneyDisplay amount={allocationTotal} />
            </span>
            <span>
              <span className="font-semibold">Unallocated amount:</span> <MoneyDisplay amount={unallocatedAmount} />
            </span>
          </div>

          {allocationValidationMessages.length ? (
            <div className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">
              {allocationValidationMessages.map((message) => (
                <p key={message}>{message}</p>
              ))}
            </div>
          ) : null}
        </fieldset>

        <label className="block text-sm font-medium text-slate-700">
          Notes
          <textarea className="mt-2 min-h-24 w-full rounded-md border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm" disabled={!canMutate} name="notes" />
        </label>

        <ActionBar>
          <Button disabled={!canMutate || hasAllocationValidationError} isLoading={createMutation.isPending} type="submit">
            Create draft payment
          </Button>
        </ActionBar>
      </FormCard>
    </div>
  );
}
