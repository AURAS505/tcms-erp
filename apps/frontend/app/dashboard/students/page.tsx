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
import { listStudents } from "@/lib/students";
import type { Student } from "@/types/students";

const columns: SimpleTableColumn<Student>[] = [
  {
    header: "Admission",
    render: (student) => (
      <Link className="font-semibold text-[#0948B3] hover:underline" href={`/dashboard/students/${student.id}`}>
        {student.admission_number}
      </Link>
    ),
  },
  { header: "Student", render: (student) => student.full_name },
  { header: "Class", render: (student) => student.current_grade_class || "Not set" },
  { header: "Contact", render: (student) => student.phone || student.email || "Not set" },
  { header: "Status", render: (student) => <StatusBadge status={student.status} /> },
];

export default function StudentsPage() {
  const [search, setSearch] = useState("");
  const { data, error, isLoading } = useQuery({
    queryKey: ["students", search],
    queryFn: () => listStudents(search),
  });

  return (
    <div className="space-y-5">
      <PageHeader
        actions={<SearchInput onChange={(event) => setSearch(event.target.value)} placeholder="Search students" value={search} />}
        description="Read-only student admission records from the backend."
        title="Students"
      />

      {isLoading ? <LoadingState label="Loading students..." /> : null}
      {error ? <ErrorState message={error instanceof Error ? error.message : undefined} /> : null}
      {data && data.data.length === 0 ? (
        <EmptyState message="No student records are available for your current branch context." title="No students found" />
      ) : null}
      {data && data.data.length > 0 ? <SimpleTable columns={columns} getRowKey={(student) => student.id} rows={data.data} /> : null}
    </div>
  );
}

