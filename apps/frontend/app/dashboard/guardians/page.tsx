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
import { listGuardians } from "@/lib/guardians";
import type { Guardian } from "@/types/guardians";

const columns: SimpleTableColumn<Guardian>[] = [
  {
    header: "Guardian",
    render: (guardian) => (
      <Link className="font-semibold text-[#0948B3] hover:underline" href={`/dashboard/guardians/${guardian.id}`}>
        {guardian.full_name}
      </Link>
    ),
  },
  { header: "Relationship", render: (guardian) => guardian.relationship_type.replaceAll("_", " ") },
  { header: "Contact", render: (guardian) => guardian.phone || guardian.email || "Not set" },
  { header: "Occupation", render: (guardian) => guardian.occupation || "Not set" },
  { header: "Status", render: (guardian) => <StatusBadge status={guardian.is_active ? "active" : "inactive"} /> },
];

export default function GuardiansPage() {
  const [search, setSearch] = useState("");
  const { data, error, isLoading } = useQuery({
    queryKey: ["guardians", search],
    queryFn: () => listGuardians(search),
  });

  return (
    <div className="space-y-5">
      <PageHeader
        actions={<SearchInput onChange={(event) => setSearch(event.target.value)} placeholder="Search guardians" value={search} />}
        description="Read-only guardian records from the backend."
        title="Guardians"
      />

      {isLoading ? <LoadingState label="Loading guardians..." /> : null}
      {error ? <ErrorState message={error instanceof Error ? error.message : undefined} /> : null}
      {data && data.data.length === 0 ? (
        <EmptyState message="No guardian records are available for your current branch context." title="No guardians found" />
      ) : null}
      {data && data.data.length > 0 ? <SimpleTable columns={columns} getRowKey={(guardian) => guardian.id} rows={data.data} /> : null}
    </div>
  );
}

