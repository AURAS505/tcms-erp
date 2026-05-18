import type { ReactNode } from "react";

interface DetailGridProps {
  children: ReactNode;
  columns?: "two" | "three" | "four";
}

interface DetailItemProps {
  label: string;
  value?: ReactNode;
}

const gridColumns: Record<NonNullable<DetailGridProps["columns"]>, string> = {
  two: "sm:grid-cols-2",
  three: "sm:grid-cols-2 lg:grid-cols-3",
  four: "sm:grid-cols-2 lg:grid-cols-4",
};

export function DetailGrid({ children, columns = "two" }: DetailGridProps) {
  return <dl className={`grid gap-4 ${gridColumns[columns]}`}>{children}</dl>;
}

export function DetailItem({ label, value }: DetailItemProps) {
  return (
    <div className="rounded-lg border border-slate-200/80 bg-[#F8FAFC] px-3 py-3">
      <dt className="text-[11px] font-bold uppercase tracking-wide text-slate-500">{label}</dt>
      <dd className="mt-1 text-sm font-medium text-slate-800">{value || "Not set"}</dd>
    </div>
  );
}
