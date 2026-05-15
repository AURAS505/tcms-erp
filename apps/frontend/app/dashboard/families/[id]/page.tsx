"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { ErrorState } from "@/components/ui/ErrorState";
import { LoadingState } from "@/components/ui/LoadingState";
import { PageHeader } from "@/components/ui/PageHeader";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { getFamily } from "@/lib/guardians";

function DetailItem({ label, value }: { label: string; value?: string | null }) {
  return (
    <div>
      <dt className="text-xs font-semibold uppercase text-slate-500">{label}</dt>
      <dd className="mt-1 text-sm text-slate-800">{value || "Not set"}</dd>
    </div>
  );
}

export default function FamilyDetailPage({ params }: { params: { id: string } }) {
  const { data: family, error, isLoading } = useQuery({
    queryKey: ["families", params.id],
    queryFn: () => getFamily(params.id),
  });

  return (
    <div className="space-y-5">
      <PageHeader
        actions={
          <Link className="rounded-md border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50" href="/dashboard/families">
            Back to families
          </Link>
        }
        description="Read-only family profile. Create, edit, and guardian linking workflows are pending."
        title={family?.family_code ?? "Family profile"}
      />

      {isLoading ? <LoadingState label="Loading family..." /> : null}
      {error ? <ErrorState message={error instanceof Error ? error.message : undefined} /> : null}

      {family ? (
        <section className="grid gap-4 lg:grid-cols-3">
          <article className="rounded-lg bg-white p-5 shadow-[0_2px_18px_rgba(38,43,64,0.08)] lg:col-span-2">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h2 className="text-lg font-semibold text-[#262B40]">{family.family_code}</h2>
                <p className="mt-1 text-sm text-slate-500">{family.primary_contact_name}</p>
              </div>
              <StatusBadge status={family.is_active ? "active" : "inactive"} />
            </div>
            <dl className="mt-6 grid gap-4 sm:grid-cols-2">
              <DetailItem label="Primary contact" value={family.primary_contact_name} />
              <DetailItem label="Contact number" value={family.primary_contact_number} />
              <DetailItem label="Created" value={family.created_at} />
              <DetailItem label="Updated" value={family.updated_at} />
            </dl>
          </article>
          <article className="rounded-lg bg-white p-5 shadow-[0_2px_18px_rgba(38,43,64,0.08)]">
            <h2 className="text-base font-semibold text-[#262B40]">Address and notes</h2>
            <dl className="mt-4 space-y-4">
              <DetailItem label="Address" value={family.address} />
              <DetailItem label="Notes" value={family.notes} />
            </dl>
          </article>
        </section>
      ) : null}
    </div>
  );
}

