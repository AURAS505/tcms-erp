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
import { listStudentInquiries } from "@/lib/students";
import type { StudentInquiry } from "@/types/students";

const columns: SimpleTableColumn<StudentInquiry>[] = [
  {
    header: "Student",
    render: (inquiry) => (
      <Link className="font-semibold text-[#0948B3] hover:underline" href={`/dashboard/student-inquiries/${inquiry.id}`}>
        {inquiry.student_full_name}
      </Link>
    ),
  },
  { header: "Guardian", render: (inquiry) => inquiry.guardian_name },
  { header: "Contact", render: (inquiry) => inquiry.contact_number || inquiry.email || "Not set" },
  { header: "Interest", render: (inquiry) => inquiry.interested_class_subject || "Not set" },
  { header: "Status", render: (inquiry) => <StatusBadge status={inquiry.status} /> },
];

export default function StudentInquiriesPage() {
  const [search, setSearch] = useState("");
  const { data, error, isLoading } = useQuery({
    queryKey: ["student-inquiries", search],
    queryFn: () => listStudentInquiries(search),
  });

  return (
    <div className="space-y-5">
      <PageHeader
        actions={<SearchInput onChange={(event) => setSearch(event.target.value)} placeholder="Search inquiries" value={search} />}
        description="Read-only inquiry records for admission follow-up."
        title="Student Inquiries"
      />

      {isLoading ? <LoadingState label="Loading inquiries..." /> : null}
      {error ? <ErrorState message={error instanceof Error ? error.message : undefined} /> : null}
      {data && data.data.length === 0 ? (
        <EmptyState message="No student inquiries are available for your current branch context." title="No inquiries found" />
      ) : null}
      {data && data.data.length > 0 ? <SimpleTable columns={columns} getRowKey={(inquiry) => inquiry.id} rows={data.data} /> : null}
    </div>
  );
}

