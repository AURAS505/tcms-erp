import type { ReactNode } from "react";

type WarningTone = "info" | "success" | "warning" | "danger" | "neutral";

interface WarningPanelProps {
  children: ReactNode;
  title?: string;
  tone?: WarningTone;
}

const tones: Record<WarningTone, string> = {
  danger: "border-red-200 bg-red-50 text-red-800",
  info: "border-blue-200 bg-blue-50 text-blue-800",
  neutral: "border-slate-200 bg-slate-50 text-slate-700",
  success: "border-green-200 bg-green-50 text-green-800",
  warning: "border-amber-200 bg-amber-50 text-amber-800",
};

const liveRegions: Record<WarningTone, { live?: "polite"; role?: "alert" | "status" }> = {
  danger: { role: "alert" },
  info: { live: "polite", role: "status" },
  neutral: {},
  success: { live: "polite", role: "status" },
  warning: { live: "polite", role: "status" },
};

export function WarningPanel({ children, title, tone = "info" }: WarningPanelProps) {
  const liveRegion = liveRegions[tone];

  return (
    <div
      aria-live={liveRegion.live}
      className={`rounded-lg border px-4 py-3 text-sm leading-6 ${tones[tone]}`}
      role={liveRegion.role}
    >
      {title ? <p className="font-bold">{title}</p> : null}
      <div className={title ? "mt-1" : ""}>{children}</div>
    </div>
  );
}
