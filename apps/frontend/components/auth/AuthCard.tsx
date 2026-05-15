import type { ReactNode } from "react";

interface AuthCardProps {
  children: ReactNode;
  subtitle: string;
  title: string;
}

export function AuthCard({ children, subtitle, title }: AuthCardProps) {
  return (
    <main className="flex min-h-screen items-center justify-center bg-[#F5F8FB] px-4 py-10">
      <section className="w-full max-w-md rounded-lg bg-white p-7 shadow-[0_2px_18px_rgba(38,43,64,0.08)]">
        <div className="mb-6 text-center">
          <div className="mx-auto mb-4 flex h-11 w-11 items-center justify-center rounded-md bg-[#262B40] text-lg font-bold text-white">
            T
          </div>
          <h1 className="text-2xl font-semibold text-[#262B40]">{title}</h1>
          <p className="mt-2 text-sm leading-6 text-slate-500">{subtitle}</p>
        </div>
        {children}
      </section>
    </main>
  );
}

