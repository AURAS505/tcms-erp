import type { ReactNode } from "react";

interface DetailCardProps {
  actions?: ReactNode;
  children: ReactNode;
  className?: string;
  description?: ReactNode;
  title: ReactNode;
}

export function DetailCard({ actions, children, className = "", description, title }: DetailCardProps) {
  return (
    <article className={`tcms-card p-5 ${className}`}>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0">
          <h2 className="text-lg font-bold text-[#262B40]">{title}</h2>
          {description ? <div className="mt-1 text-sm leading-6 text-slate-500">{description}</div> : null}
        </div>
        {actions ? <div className="shrink-0">{actions}</div> : null}
      </div>
      <div className="mt-5">{children}</div>
    </article>
  );
}
