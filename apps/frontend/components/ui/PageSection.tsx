import type { ReactNode } from "react";

interface PageSectionProps {
  actions?: ReactNode;
  children: ReactNode;
  description?: string;
  title?: string;
}

export function PageSection({ actions, children, description, title }: PageSectionProps) {
  return (
    <section className="tcms-card p-5">
      {title || description || actions ? (
        <div className="mb-5 flex flex-col gap-3 border-b border-slate-200/80 pb-4 sm:flex-row sm:items-start sm:justify-between">
          <div>
            {title ? <h2 className="text-base font-bold text-[#262B40]">{title}</h2> : null}
            {description ? <p className="mt-1 text-sm leading-6 text-slate-600">{description}</p> : null}
          </div>
          {actions ? <div className="flex flex-wrap items-center gap-2 sm:justify-end">{actions}</div> : null}
        </div>
      ) : null}
      {children}
    </section>
  );
}
