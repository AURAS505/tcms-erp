"use client";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  if (process.env.NEXT_PUBLIC_APP_ENV !== "production") {
    console.error(error);
  }

  return (
    <html lang="en">
      <body>
        <main className="flex min-h-screen items-center justify-center bg-slate-50 px-6">
          <section className="max-w-md rounded-lg border border-slate-200 bg-white p-6 text-center shadow-sm">
            <p className="text-sm font-semibold uppercase text-slate-500">Application error</p>
            <h1 className="mt-2 text-2xl font-semibold text-slate-900">Something went wrong</h1>
            <p className="mt-3 text-sm leading-6 text-slate-600">
              The request could not be completed. Try again, or contact support if the issue continues.
            </p>
            <button
              className="mt-6 rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800"
              onClick={reset}
              type="button"
            >
              Try again
            </button>
          </section>
        </main>
      </body>
    </html>
  );
}
