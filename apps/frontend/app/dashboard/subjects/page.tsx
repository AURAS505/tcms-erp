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
import { listSubjects } from "@/lib/classes";
import type { Subject } from "@/types/classes";

const columns: SimpleTableColumn<Subject>[] = [
  {
    header: "Code",
    render: (subject) => (
      <Link className="font-semibold text-[#0948B3] hover:underline" href={`/dashboard/subjects/${subject.id}`}>
        {subject.subject_code}
      </Link>
    ),
  },
  { header: "Subject", render: (subject) => subject.subject_name },
  { header: "Description", render: (subject) => subject.description || "Not set" },
  { header: "Status", render: (subject) => <StatusBadge status={subject.is_active ? "active" : "inactive"} /> },
];

export default function SubjectsPage() {
  const [search, setSearch] = useState("");
  const { data, error, isLoading } = useQuery({
    queryKey: ["subjects", search],
    queryFn: () => listSubjects(search),
  });

  return (
    <div className="space-y-5">
      <PageHeader
        actions={<SearchInput onChange={(event) => setSearch(event.target.value)} placeholder="Search subjects" value={search} />}
        description="Read-only subject catalog from the backend."
        title="Subjects"
      />

      {isLoading ? <LoadingState label="Loading subjects..." /> : null}
      {error ? <ErrorState message={error instanceof Error ? error.message : undefined} /> : null}
      {data && data.data.length === 0 ? <EmptyState message="No subjects are available yet." title="No subjects found" /> : null}
      {data && data.data.length > 0 ? <SimpleTable columns={columns} getRowKey={(subject) => subject.id} rows={data.data} /> : null}
    </div>
  );
}
