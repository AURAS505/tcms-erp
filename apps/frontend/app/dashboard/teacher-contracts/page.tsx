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
import { listTeacherContracts } from "@/lib/teachers";
import type { TeacherContract } from "@/types/teachers";

const formatContractType = (value: string) =>
  value
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");

const columns: SimpleTableColumn<TeacherContract>[] = [
  {
    header: "Contract",
    render: (contract) => (
      <Link className="font-semibold text-[#0948B3] hover:underline" href={`/dashboard/teacher-contracts/${contract.id}`}>
        {contract.id}
      </Link>
    ),
  },
  { header: "Teacher", render: (contract) => contract.teacher },
  { header: "Type", render: (contract) => formatContractType(contract.contract_type) },
  { header: "Effective from", render: (contract) => contract.effective_from_ad },
  { header: "Status", render: (contract) => <StatusBadge status={contract.is_active ? "active" : "inactive"} /> },
];

export default function TeacherContractsPage() {
  const [search, setSearch] = useState("");
  const { data, error, isLoading } = useQuery({
    queryKey: ["teacher-contracts", search],
    queryFn: () => listTeacherContracts(search),
  });

  return (
    <div className="space-y-5">
      <PageHeader
        actions={<SearchInput onChange={(event) => setSearch(event.target.value)} placeholder="Search teacher contracts" value={search} />}
        description="Read-only teacher contract records from the backend."
        title="Teacher Contracts"
      />

      {isLoading ? <LoadingState label="Loading teacher contracts..." /> : null}
      {error ? <ErrorState message={error instanceof Error ? error.message : undefined} /> : null}
      {data && data.data.length === 0 ? (
        <EmptyState message="No teacher contract records are available for your current branch context." title="No teacher contracts found" />
      ) : null}
      {data && data.data.length > 0 ? (
        <SimpleTable columns={columns} getRowKey={(contract) => contract.id} rows={data.data} />
      ) : null}
    </div>
  );
}
