const statusStyles: Record<string, string> = {
  active: "bg-green-50 text-green-700",
  appointment_scheduled: "bg-blue-50 text-blue-700",
  approved: "bg-green-50 text-green-700",
  cancelled: "bg-slate-100 text-slate-700",
  closed: "bg-slate-100 text-slate-700",
  contacted: "bg-blue-50 text-blue-700",
  converted: "bg-green-50 text-green-700",
  completed: "bg-indigo-50 text-indigo-700",
  draft: "bg-slate-100 text-slate-700",
  graduated: "bg-indigo-50 text-indigo-700",
  inactive: "bg-slate-100 text-slate-700",
  inquiry: "bg-blue-50 text-blue-700",
  left: "bg-orange-50 text-orange-700",
  new: "bg-blue-50 text-blue-700",
  on_break: "bg-yellow-50 text-yellow-700",
  on_leave: "bg-yellow-50 text-yellow-700",
  open: "bg-blue-50 text-blue-700",
  paid: "bg-green-50 text-green-700",
  partial: "bg-yellow-50 text-yellow-700",
  paused: "bg-yellow-50 text-yellow-700",
  posted: "bg-green-50 text-green-700",
  pending: "bg-yellow-50 text-yellow-700",
  pending_approval: "bg-yellow-50 text-yellow-700",
  pending_review: "bg-yellow-50 text-yellow-700",
  rejected: "bg-red-50 text-red-700",
  refunded: "bg-indigo-50 text-indigo-700",
  resigned: "bg-orange-50 text-orange-700",
  reversed: "bg-red-50 text-red-700",
  submitted: "bg-blue-50 text-blue-700",
  terminated: "bg-red-50 text-red-700",
  unpaid: "bg-orange-50 text-orange-700",
  voided: "bg-red-50 text-red-700",
  waived: "bg-indigo-50 text-indigo-700",
  written_off: "bg-slate-100 text-slate-700",
};

const formatStatus = (status: string) =>
  status
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");

export function StatusBadge({ status }: { status: string }) {
  return (
    <span className={`inline-flex rounded-full px-2.5 py-1 text-xs font-semibold ${statusStyles[status] ?? statusStyles.closed}`}>
      {formatStatus(status)}
    </span>
  );
}
