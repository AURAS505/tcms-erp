interface EmptyStateProps {
  message?: string;
  title: string;
}

export function EmptyState({ message, title }: EmptyStateProps) {
  return (
    <div className="rounded-lg border border-dashed border-slate-300 bg-white p-8 text-center">
      <h2 className="text-base font-semibold text-[#262B40]">{title}</h2>
      {message ? <p className="mt-2 text-sm text-slate-500">{message}</p> : null}
    </div>
  );
}

