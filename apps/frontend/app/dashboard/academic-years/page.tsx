"use client";

import Link from "next/link";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState } from "@/components/ui/ErrorState";
import { LoadingState } from "@/components/ui/LoadingState";
import { PageHeader } from "@/components/ui/PageHeader";
import { SearchInput } from "@/components/ui/SearchInput";
import { SimpleTable, type SimpleTableColumn } from "@/components/ui/SimpleTable";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { listAcademicYears } from "@/lib/academic";
import type { AcademicYear } from "@/types/academic";

const columns: SimpleTableColumn<AcademicYear>[] = [
  {
    header: "Academic year",
    render: (year) => (
      <Link className="font-semibold text-[#0948B3] hover:underline" href={`/dashboard/academic-years/${year.id}`}>
        {year.name}
      </Link>
    ),
  },
  { header: "AD range", render: (year) => `${year.ad_start_date} to ${year.ad_end_date}` },
  { header: "BS range", render: (year) => `${year.bs_start_date} to ${year.bs_end_date}` },
  { header: "Active", render: (year) => (year.is_active ? "Yes" : "No") },
  { header: "Status", render: (year) => <StatusBadge status={year.status} /> },
];

export default function AcademicYearsPage() {
  const [search, setSearch] = useState("");
  const { data, error, isLoading } = useQuery({
    queryKey: ["academic-years", search],
    queryFn: () => listAcademicYears(search),
  });

  return (
    <div className="space-y-5">
      <PageHeader
        actions={<SearchInput onChange={(event) => setSearch(event.target.value)} placeholder="Search academic years" value={search} />}
        description="Read academic years and access close controls from year detail pages."
        title="Academic Years"
      />
      {isLoading ? <LoadingState label="Loading academic years..." /> : null}
      {error ? <ErrorState message={error instanceof Error ? error.message : undefined} /> : null}
      {data && data.data.length === 0 ? <EmptyState message="No academic years are available." title="No academic years found" /> : null}
      {data && data.data.length > 0 ? <SimpleTable columns={columns} getRowKey={(year) => year.id} rows={data.data} /> : null}
    </div>
  );
}
