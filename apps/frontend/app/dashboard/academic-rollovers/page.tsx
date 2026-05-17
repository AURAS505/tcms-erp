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
import { useAuth } from "@/hooks/useAuth";
import { listAcademicRollovers } from "@/lib/academic";
import type { AcademicYearRollover } from "@/types/academic";
import type { Role } from "@/types/auth";

const rolloverRoles: Role[] = ["super_admin", "institute_owner", "accountant"];

const columns: SimpleTableColumn<AcademicYearRollover>[] = [
  {
    header: "Rollover",
    render: (rollover) => (
      <Link className="font-semibold text-[#0948B3] hover:underline" href={`/dashboard/academic-rollovers/${rollover.id}`}>
        {rollover.id}
      </Link>
    ),
  },
  { header: "Source year", render: (rollover) => rollover.from_academic_year },
  { header: "Target year", render: (rollover) => rollover.to_academic_year || "Not created" },
  { header: "Trial balance", render: (rollover) => (rollover.trial_balance_validated ? "Validated" : "Pending") },
  { header: "Status", render: (rollover) => <StatusBadge status={rollover.status} /> },
];

export default function AcademicRolloversPage() {
  const [search, setSearch] = useState("");
  const { hasRole } = useAuth();
  const canMutate = rolloverRoles.some((role) => hasRole(role));
  const { data, error, isLoading } = useQuery({
    queryKey: ["academic-rollovers", search],
    queryFn: () => listAcademicRollovers(search),
  });

  return (
    <div className="space-y-5">
      <PageHeader
        actions={
          <div className="flex flex-wrap items-center gap-2">
            <SearchInput onChange={(event) => setSearch(event.target.value)} placeholder="Search rollovers" value={search} />
            {canMutate ? (
              <Link className="rounded-md bg-[#0948B3] px-3 py-2 text-sm font-semibold text-white hover:bg-[#073a91]" href="/dashboard/academic-rollovers/new">
                New Rollover
              </Link>
            ) : null}
          </div>
        }
        description="High-risk academic year rollover workflow. Closing and opening entries are generated only by the backend."
        title="Academic Rollovers"
      />
      {isLoading ? <LoadingState label="Loading academic rollovers..." /> : null}
      {error ? <ErrorState message={error instanceof Error ? error.message : undefined} /> : null}
      {data && data.data.length === 0 ? <EmptyState message="No academic rollovers are available." title="No academic rollovers found" /> : null}
      {data && data.data.length > 0 ? <SimpleTable columns={columns} getRowKey={(rollover) => rollover.id} rows={data.data} /> : null}
    </div>
  );
}
