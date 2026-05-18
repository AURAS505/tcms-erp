import type { ReactNode } from "react";

interface ActionBarProps {
  children: ReactNode;
  align?: "between" | "end";
}

export function ActionBar({ align = "end", children }: ActionBarProps) {
  return (
    <div
      className={`flex flex-col-reverse gap-2 border-t border-slate-200/80 pt-4 sm:flex-row sm:flex-wrap ${
        align === "between" ? "sm:items-center sm:justify-between" : "sm:items-center sm:justify-end"
      }`}
    >
      {children}
    </div>
  );
}
