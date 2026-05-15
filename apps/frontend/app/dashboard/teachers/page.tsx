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
import { listTeachers } from "@/lib/teachers";
import type { Teacher } from "@/types/teachers";

const columns: SimpleTableColumn<Teacher>[] = [
  {
    header: "Employee",
    render: (teacher) => (
      <Link className="font-semibold text-[#0948B3] hover:underline" href={`/dashboard/teachers/${teacher.id}`}>
        {teacher.employee_number}
      </Link>
    ),
  },
  { header: "Teacher", render: (teacher) => teacher.full_name },
  { header: "Specialization", render: (teacher) => teacher.specialization || "Not set" },
  { header: "Contact", render: (teacher) => teacher.phone || teacher.email || "Not set" },
  { header: "Status", render: (teacher) => <StatusBadge status={teacher.status} /> },
];

export default function TeachersPage() {
  const [search, setSearch] = useState("");
  const { data, error, isLoading } = useQuery({
    queryKey: ["teachers", search],
    queryFn: () => listTeachers(search),
  });

  return (
    <div className="space-y-5">
      <PageHeader
        actions={<SearchInput onChange={(event) => setSearch(event.target.value)} placeholder="Search teachers" value={search} />}
        description="Read-only teacher records from the backend."
        title="Teachers"
      />

      {isLoading ? <LoadingState label="Loading teachers..." /> : null}
      {error ? <ErrorState message={error instanceof Error ? error.message : undefined} /> : null}
      {data && data.data.length === 0 ? (
        <EmptyState message="No teacher records are available for your current branch context." title="No teachers found" />
      ) : null}
      {data && data.data.length > 0 ? <SimpleTable columns={columns} getRowKey={(teacher) => teacher.id} rows={data.data} /> : null}
    </div>
  );
}
