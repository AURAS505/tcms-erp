import type { FormHTMLAttributes, ReactNode } from "react";

interface FormCardProps extends FormHTMLAttributes<HTMLFormElement> {
  children: ReactNode;
  description?: string;
  title?: string;
}

export function FormCard({ children, className = "", description, title, ...props }: FormCardProps) {
  return (
    <form className={`tcms-card space-y-5 p-4 sm:p-5 ${className}`} {...props}>
      {title || description ? (
        <div className="border-b border-slate-200/80 pb-4">
          {title ? <h2 className="text-base font-bold text-[#262B40]">{title}</h2> : null}
          {description ? <p className="mt-1 text-sm leading-6 text-slate-600">{description}</p> : null}
        </div>
      ) : null}
      {children}
    </form>
  );
}
