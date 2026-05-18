const statusStyles: Record<string, string> = {
  active: "border-green-200 bg-green-50 text-green-700",
  appointment_scheduled: "border-blue-200 bg-blue-50 text-blue-700",
  approved: "border-green-200 bg-green-50 text-green-700",
  balanced: "border-green-200 bg-green-50 text-green-700",
  cancelled: "border-slate-200 bg-slate-100 text-slate-700",
  closed: "border-slate-200 bg-slate-100 text-slate-700",
  contacted: "border-blue-200 bg-blue-50 text-blue-700",
  converted: "border-green-200 bg-green-50 text-green-700",
  completed: "border-indigo-200 bg-indigo-50 text-indigo-700",
  draft: "border-slate-200 bg-slate-100 text-slate-700",
  graduated: "border-indigo-200 bg-indigo-50 text-indigo-700",
  hard_closed: "border-slate-300 bg-slate-100 text-slate-800",
  inactive: "border-slate-200 bg-slate-100 text-slate-700",
  inquiry: "border-blue-200 bg-blue-50 text-blue-700",
  left: "border-orange-200 bg-orange-50 text-orange-700",
  new: "border-blue-200 bg-blue-50 text-blue-700",
  on_break: "border-yellow-200 bg-yellow-50 text-yellow-800",
  on_leave: "border-yellow-200 bg-yellow-50 text-yellow-800",
  open: "border-blue-200 bg-blue-50 text-blue-700",
  out_of_balance: "border-red-200 bg-red-50 text-red-700",
  paid: "border-green-200 bg-green-50 text-green-700",
  partial: "border-yellow-200 bg-yellow-50 text-yellow-800",
  paused: "border-yellow-200 bg-yellow-50 text-yellow-800",
  posted: "border-green-200 bg-green-50 text-green-700",
  pending: "border-yellow-200 bg-yellow-50 text-yellow-800",
  pending_approval: "border-yellow-200 bg-yellow-50 text-yellow-800",
  pending_review: "border-yellow-200 bg-yellow-50 text-yellow-800",
  ready: "border-blue-200 bg-blue-50 text-blue-700",
  rejected: "border-red-200 bg-red-50 text-red-700",
  refunded: "border-indigo-200 bg-indigo-50 text-indigo-700",
  resigned: "border-orange-200 bg-orange-50 text-orange-700",
  reversed: "border-red-200 bg-red-50 text-red-700",
  soft_closed: "border-yellow-200 bg-yellow-50 text-yellow-800",
  submitted: "border-blue-200 bg-blue-50 text-blue-700",
  terminated: "border-red-200 bg-red-50 text-red-700",
  unpaid: "border-orange-200 bg-orange-50 text-orange-700",
  voided: "border-red-200 bg-red-50 text-red-700",
  waived: "border-indigo-200 bg-indigo-50 text-indigo-700",
  written_off: "border-slate-200 bg-slate-100 text-slate-700",
};

const formatStatus = (status: string) =>
  status
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");

export function StatusBadge({ status }: { status: string }) {
  return (
    <span className={`inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-bold leading-none ${statusStyles[status] ?? statusStyles.closed}`}>
      {formatStatus(status)}
    </span>
  );
}
