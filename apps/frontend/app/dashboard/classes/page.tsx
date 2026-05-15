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
import { listClasses } from "@/lib/classes";
import type { ClassRoom } from "@/types/classes";

const columns: SimpleTableColumn<ClassRoom>[] = [
  {
    header: "Class",
    render: (classRoom) => (
      <Link className="font-semibold text-[#0948B3] hover:underline" href={`/dashboard/classes/${classRoom.id}`}>
        {classRoom.class_name}
      </Link>
    ),
  },
  { header: "Batch", render: (classRoom) => classRoom.batch_name || "Not set" },
  { header: "Section", render: (classRoom) => classRoom.section_name || "Not set" },
  { header: "Capacity", render: (classRoom) => classRoom.capacity ?? "Not set" },
  { header: "Monthly fee", render: (classRoom) => classRoom.monthly_fee ?? "Not set" },
  { header: "Status", render: (classRoom) => <StatusBadge status={classRoom.status} /> },
];

export default function ClassesPage() {
  const [search, setSearch] = useState("");
  const { data, error, isLoading } = useQuery({
    queryKey: ["classes", search],
    queryFn: () => listClasses(search),
  });

  return (
    <div className="space-y-5">
      <PageHeader
        actions={<SearchInput onChange={(event) => setSearch(event.target.value)} placeholder="Search classes" value={search} />}
        description="Read-only class records from the backend."
        title="Classes"
      />

      {isLoading ? <LoadingState label="Loading classes..." /> : null}
      {error ? <ErrorState message={error instanceof Error ? error.message : undefined} /> : null}
      {data && data.data.length === 0 ? (
        <EmptyState message="No class records are available for your current branch context." title="No classes found" />
      ) : null}
      {data && data.data.length > 0 ? (
        <SimpleTable columns={columns} getRowKey={(classRoom) => classRoom.id} rows={data.data} />
      ) : null}
    </div>
  );
}
