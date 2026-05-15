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
import { listFamilies } from "@/lib/guardians";
import type { Family } from "@/types/guardians";

const columns: SimpleTableColumn<Family>[] = [
  {
    header: "Family",
    render: (family) => (
      <Link className="font-semibold text-[#0948B3] hover:underline" href={`/dashboard/families/${family.id}`}>
        {family.family_code}
      </Link>
    ),
  },
  { header: "Primary contact", render: (family) => family.primary_contact_name },
  { header: "Contact number", render: (family) => family.primary_contact_number },
  { header: "Address", render: (family) => family.address || "Not set" },
  { header: "Status", render: (family) => <StatusBadge status={family.is_active ? "active" : "inactive"} /> },
];

export default function FamiliesPage() {
  const [search, setSearch] = useState("");
  const { data, error, isLoading } = useQuery({
    queryKey: ["families", search],
    queryFn: () => listFamilies(search),
  });

  return (
    <div className="space-y-5">
      <PageHeader
        actions={<SearchInput onChange={(event) => setSearch(event.target.value)} placeholder="Search families" value={search} />}
        description="Read-only family records from the backend."
        title="Families"
      />

      {isLoading ? <LoadingState label="Loading families..." /> : null}
      {error ? <ErrorState message={error instanceof Error ? error.message : undefined} /> : null}
      {data && data.data.length === 0 ? (
        <EmptyState message="No family records are available for your current branch context." title="No families found" />
      ) : null}
      {data && data.data.length > 0 ? <SimpleTable columns={columns} getRowKey={(family) => family.id} rows={data.data} /> : null}
    </div>
  );
}

