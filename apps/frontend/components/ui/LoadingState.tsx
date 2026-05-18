export function LoadingState({ label = "Loading..." }: { label?: string }) {
  return (
    <div aria-live="polite" className="tcms-card p-5" role="status">
      <div className="flex items-center gap-3">
        <span className="h-2.5 w-2.5 animate-pulse rounded-full bg-[#0948B3]" />
        <span className="text-sm font-semibold text-slate-600">{label}</span>
      </div>
      <div className="mt-4 grid gap-2">
        <div className="h-2 rounded-full bg-slate-100" />
        <div className="h-2 w-2/3 rounded-full bg-slate-100" />
      </div>
    </div>
  );
}

