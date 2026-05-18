"use client";

import Link from "next/link";
import { useRouteId } from "@/hooks/useRouteId";
import { useQuery } from "@tanstack/react-query";
import { ErrorState } from "@/components/ui/ErrorState";
import { LoadingState } from "@/components/ui/LoadingState";
import { PageHeader } from "@/components/ui/PageHeader";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { getGuardian } from "@/lib/guardians";

function DetailItem({ label, value }: { label: string; value?: string | null }) {
  return (
    <div>
      <dt className="text-xs font-semibold uppercase text-slate-500">{label}</dt>
      <dd className="mt-1 text-sm text-slate-800">{value || "Not set"}</dd>
    </div>
  );
}

export default function GuardianDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const id = useRouteId(params);
  const { data: guardian, error, isLoading } = useQuery({
    enabled: Boolean(id),
    queryKey: ["guardians", id],
    queryFn: () => getGuardian(id),
  });

  return (
    <div className="space-y-5">
      <PageHeader
        actions={
          <Link className="rounded-md border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50" href="/dashboard/guardians">
            Back to guardians
          </Link>
        }
        description="Read-only guardian profile. Create, edit, and linking workflows are pending."
        title={guardian?.full_name ?? "Guardian profile"}
      />

      {isLoading ? <LoadingState label="Loading guardian..." /> : null}
      {error ? <ErrorState message={error instanceof Error ? error.message : undefined} /> : null}

      {guardian ? (
        <section className="grid gap-4 lg:grid-cols-3">
          <article className="rounded-lg bg-white p-5 shadow-[0_2px_18px_rgba(38,43,64,0.08)] lg:col-span-2">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h2 className="text-lg font-semibold text-[#262B40]">{guardian.full_name}</h2>
                <p className="mt-1 text-sm capitalize text-slate-500">{guardian.relationship_type.replaceAll("_", " ")}</p>
              </div>
              <StatusBadge status={guardian.is_active ? "active" : "inactive"} />
            </div>
            <dl className="mt-6 grid gap-4 sm:grid-cols-2">
              <DetailItem label="Phone" value={guardian.phone} />
              <DetailItem label="Alternate phone" value={guardian.alternate_phone} />
              <DetailItem label="Email" value={guardian.email} />
              <DetailItem label="Occupation" value={guardian.occupation} />
              <DetailItem label="Primary contact" value={guardian.is_primary_contact ? "Yes" : "No"} />
              <DetailItem label="Family ID" value={guardian.family} />
            </dl>
          </article>
          <article className="rounded-lg bg-white p-5 shadow-[0_2px_18px_rgba(38,43,64,0.08)]">
            <h2 className="text-base font-semibold text-[#262B40]">Address</h2>
            <p className="mt-4 text-sm leading-6 text-slate-700">{guardian.address || "No address recorded."}</p>
          </article>
        </section>
      ) : null}
    </div>
  );
}

