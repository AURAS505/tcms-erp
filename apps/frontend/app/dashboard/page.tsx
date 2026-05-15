const cards = [
  ["Active students", "Pending module", "Student operations arrive in a later step."],
  ["Open approvals", "Backend guarded", "Maker-checker flows remain backend-authoritative."],
  ["Branch context", "Session based", "Navigation will expand from role permissions."],
];

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <section>
        <h1 className="text-2xl font-semibold text-[#262B40]">Dashboard</h1>
        <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-600">
          This is the protected shell foundation for TCMS ERP. Operational and financial widgets are intentionally
          placeholders until their backend modules are implemented.
        </p>
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        {cards.map(([title, value, description]) => (
          <article className="rounded-lg bg-white p-5 shadow-[0_2px_18px_rgba(38,43,64,0.08)]" key={title}>
            <p className="text-sm font-medium text-slate-500">{title}</p>
            <h2 className="mt-3 text-xl font-semibold text-[#262B40]">{value}</h2>
            <p className="mt-2 text-sm leading-6 text-slate-500">{description}</p>
          </article>
        ))}
      </section>

      <section className="rounded-lg bg-white p-5 shadow-[0_2px_18px_rgba(38,43,64,0.08)]">
        <div className="flex items-center justify-between gap-4">
          <div>
            <h2 className="text-base font-semibold text-[#262B40]">Next modules</h2>
            <p className="mt-1 text-sm text-slate-500">Student, teacher, billing, payroll, and accounting pages are pending.</p>
          </div>
          <span className="rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold text-[#0948B3]">Foundation only</span>
        </div>
      </section>
    </div>
  );
}

