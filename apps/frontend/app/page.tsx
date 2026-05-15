export default function HomePage() {
  return (
    <main className="min-h-screen bg-slate-50 px-6 py-10">
      <section className="mx-auto max-w-5xl">
        <p className="text-sm font-medium uppercase tracking-wide text-slate-500">TCMS ERP</p>
        <h1 className="mt-3 text-3xl font-semibold text-slate-950">Foundation workspace</h1>
        <p className="mt-4 max-w-2xl text-base leading-7 text-slate-700">
          This Step 1 skeleton establishes the monorepo, Docker services, Django backend, and Next.js frontend.
          Business modules and financial workflows will be implemented only after the architecture and database design
          are reviewed.
        </p>
      </section>
    </main>
  );
}
