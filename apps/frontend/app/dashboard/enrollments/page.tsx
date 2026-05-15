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
import { listClassEnrollments } from "@/lib/classes";
import type { ClassEnrollment } from "@/types/classes";

const columns: SimpleTableColumn<ClassEnrollment>[] = [
  {
    header: "Enrollment",
    render: (enrollment) => (
      <Link className="font-semibold text-[#0948B3] hover:underline" href={`/dashboard/enrollments/${enrollment.id}`}>
        {enrollment.id}
      </Link>
    ),
  },
  { header: "Student", render: (enrollment) => enrollment.student },
  { header: "Class", render: (enrollment) => enrollment.class_room },
  { header: "Joined", render: (enrollment) => enrollment.joined_date_ad || "Not set" },
  { header: "Status", render: (enrollment) => <StatusBadge status={enrollment.status} /> },
];

export default function EnrollmentsPage() {
  const [search, setSearch] = useState("");
  const { data, error, isLoading } = useQuery({
    queryKey: ["class-enrollments", search],
    queryFn: () => listClassEnrollments(search),
  });

  return (
    <div className="space-y-5">
      <PageHeader
        actions={<SearchInput onChange={(event) => setSearch(event.target.value)} placeholder="Search enrollments" value={search} />}
        description="Read-only class enrollment records from the backend."
        title="Enrollments"
      />

      {isLoading ? <LoadingState label="Loading enrollments..." /> : null}
      {error ? <ErrorState message={error instanceof Error ? error.message : undefined} /> : null}
      {data && data.data.length === 0 ? (
        <EmptyState message="No enrollment records are available for your current branch context." title="No enrollments found" />
      ) : null}
      {data && data.data.length > 0 ? (
        <SimpleTable columns={columns} getRowKey={(enrollment) => enrollment.id} rows={data.data} />
      ) : null}
    </div>
  );
}
