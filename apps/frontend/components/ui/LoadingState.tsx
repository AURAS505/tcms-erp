export function LoadingState({ label = "Loading..." }: { label?: string }) {
  return (
    <div aria-live="polite" className="rounded-lg bg-white p-6 text-sm text-slate-600 shadow-[0_2px_18px_rgba(38,43,64,0.08)]" role="status">
      {label}
    </div>
  );
}

