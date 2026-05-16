"use client";

import { FormEvent, useMemo, useState } from "react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/Button";
import { listAcademicPeriods, listAcademicYears, listBranches, listOrganizations } from "@/lib/lookups";

interface ReportFiltersProps {
  showAcademicPeriod?: boolean;
}

export function ReportFilters({ showAcademicPeriod = false }: ReportFiltersProps) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const organization = searchParams.get("organization") ?? "";
  const academicYear = searchParams.get("academic_year") ?? "";
  const [organizationValue, setOrganizationValue] = useState(organization);
  const [branchValue, setBranchValue] = useState(searchParams.get("branch") ?? "");
  const [academicYearValue, setAcademicYearValue] = useState(academicYear);
  const [academicPeriodValue, setAcademicPeriodValue] = useState(searchParams.get("academic_period") ?? "");
  const [dateFromValue, setDateFromValue] = useState(searchParams.get("date_from") ?? "");
  const [dateToValue, setDateToValue] = useState(searchParams.get("date_to") ?? "");

  const organizations = useQuery({ queryKey: ["lookup-organizations"], queryFn: listOrganizations });
  const branches = useQuery({ queryKey: ["lookup-branches"], queryFn: listBranches });
  const academicYears = useQuery({ queryKey: ["lookup-academic-years"], queryFn: listAcademicYears });
  const academicPeriods = useQuery({
    queryKey: ["lookup-academic-periods"],
    queryFn: listAcademicPeriods,
    enabled: showAcademicPeriod,
  });

  const branchOptions = useMemo(
    () => branches.data?.data.filter((branch) => !organizationValue || branch.organization === organizationValue) ?? [],
    [branches.data, organizationValue],
  );
  const academicYearOptions = useMemo(
    () => academicYears.data?.data.filter((year) => !organizationValue || year.organization === organizationValue) ?? [],
    [academicYears.data, organizationValue],
  );
  const academicPeriodOptions = useMemo(
    () => academicPeriods.data?.data.filter((period) => (!organizationValue || period.organization === organizationValue) && (!academicYearValue || period.academic_year === academicYearValue)) ?? [],
    [academicPeriods.data, academicYearValue, organizationValue],
  );

  function applyFilters(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const nextParams = new URLSearchParams();
    Object.entries({
      organization: organizationValue,
      branch: branchValue,
      academic_year: academicYearValue,
      academic_period: academicPeriodValue,
      date_from: dateFromValue,
      date_to: dateToValue,
    }).forEach(([key, value]) => {
      if (value) nextParams.set(key, value);
    });
    router.push(nextParams.toString() ? `${pathname}?${nextParams}` : pathname);
  }

  return (
    <form className="rounded-lg bg-white p-4 shadow-[0_2px_18px_rgba(38,43,64,0.08)]" onSubmit={applyFilters}>
      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-6">
        <label className="space-y-1 text-sm font-medium text-slate-700">
          <span>Organization</span>
          <select
            className="w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
            name="organization"
            value={organizationValue}
            onChange={(event) => {
              setOrganizationValue(event.target.value);
              setBranchValue("");
              setAcademicYearValue("");
              setAcademicPeriodValue("");
            }}
          >
            <option value="">Select organization</option>
            {organizations.data?.data.map((option) => (
              <option key={option.id} value={option.id}>
                {option.display_name || option.legal_name}
              </option>
            ))}
          </select>
        </label>
        <label className="space-y-1 text-sm font-medium text-slate-700">
          <span>Branch</span>
          <select className="w-full rounded-md border border-slate-200 px-3 py-2 text-sm" name="branch" value={branchValue} onChange={(event) => setBranchValue(event.target.value)}>
            <option value="">All branches</option>
            {branchOptions.map((option) => (
              <option key={option.id} value={option.id}>
                {option.name}
              </option>
            ))}
          </select>
        </label>
        <label className="space-y-1 text-sm font-medium text-slate-700">
          <span>Academic year</span>
          <select
            className="w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
            name="academic_year"
            value={academicYearValue}
            onChange={(event) => {
              setAcademicYearValue(event.target.value);
              setAcademicPeriodValue("");
            }}
          >
            <option value="">Any year</option>
            {academicYearOptions.map((option) => (
              <option key={option.id} value={option.id}>
                {option.name}
              </option>
            ))}
          </select>
        </label>
        {showAcademicPeriod ? (
          <label className="space-y-1 text-sm font-medium text-slate-700">
            <span>Academic period</span>
            <select className="w-full rounded-md border border-slate-200 px-3 py-2 text-sm" name="academic_period" value={academicPeriodValue} onChange={(event) => setAcademicPeriodValue(event.target.value)}>
              <option value="">Any period</option>
              {academicPeriodOptions.map((option) => (
                <option key={option.id} value={option.id}>
                  {option.name}
                </option>
              ))}
            </select>
          </label>
        ) : null}
        <label className="space-y-1 text-sm font-medium text-slate-700">
          <span>Date from</span>
          <input className="w-full rounded-md border border-slate-200 px-3 py-2 text-sm" name="date_from" type="date" value={dateFromValue} onChange={(event) => setDateFromValue(event.target.value)} />
        </label>
        <label className="space-y-1 text-sm font-medium text-slate-700">
          <span>Date to</span>
          <input className="w-full rounded-md border border-slate-200 px-3 py-2 text-sm" name="date_to" type="date" value={dateToValue} onChange={(event) => setDateToValue(event.target.value)} />
        </label>
      </div>
      <div className="mt-4 flex flex-wrap gap-2">
        <Button type="submit">Apply filters</Button>
        <Button type="button" variant="secondary" onClick={() => router.push(pathname)}>
          Clear
        </Button>
      </div>
      {organizations.isLoading || branches.isLoading || academicYears.isLoading ? (
        <p className="mt-3 text-sm text-slate-500">Loading filter options...</p>
      ) : null}
    </form>
  );
}
