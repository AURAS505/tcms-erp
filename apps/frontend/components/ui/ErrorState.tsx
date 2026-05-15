interface ErrorStateProps {
  message?: string;
  title?: string;
}

export function ErrorState({ message = "Unable to load this data.", title = "Something went wrong" }: ErrorStateProps) {
  return (
    <div className="rounded-lg border border-red-100 bg-red-50 p-5">
      <h2 className="text-sm font-semibold text-red-800">{title}</h2>
      <p className="mt-1 text-sm text-red-700">{message}</p>
    </div>
  );
}

