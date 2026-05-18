interface ErrorStateProps {
  message?: string;
  title?: string;
}

export function ErrorState({ message = "Unable to load this data.", title = "Something went wrong" }: ErrorStateProps) {
  return (
    <div
      aria-live="assertive"
      className="rounded-lg border border-red-200 bg-red-50 p-5 shadow-[0_2px_18px_rgba(250,82,82,0.08)]"
      role="alert"
    >
      <div className="flex gap-3">
        <span aria-hidden="true" className="mt-1 h-2.5 w-2.5 shrink-0 rounded-full bg-red-500" />
        <div>
          <h2 className="text-sm font-bold text-red-800">{title}</h2>
          <p className="mt-1 text-sm leading-6 text-red-700">{message}</p>
        </div>
      </div>
    </div>
  );
}

