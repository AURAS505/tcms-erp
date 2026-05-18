interface EmptyStateProps {
  message?: string;
  title: string;
}

export function EmptyState({ message, title }: EmptyStateProps) {
  return (
    <div className="tcms-card border-dashed p-6 text-center sm:p-8">
      <div className="mx-auto mb-4 h-10 w-10 rounded-full bg-[#F0F3FF]" />
      <h2 className="text-base font-bold text-[#262B40]">{title}</h2>
      {message ? <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-slate-500">{message}</p> : null}
    </div>
  );
}

