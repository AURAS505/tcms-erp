import type { ButtonHTMLAttributes, ReactNode } from "react";

type ButtonVariant = "primary" | "secondary" | "danger" | "ghost";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  isLoading?: boolean;
  variant?: ButtonVariant;
}

const variants: Record<ButtonVariant, string> = {
  primary: "border border-[#0948B3] bg-[#0948B3] text-white shadow-sm hover:bg-[#073a91]",
  secondary: "border border-slate-200 bg-white text-slate-800 shadow-sm hover:border-slate-300 hover:bg-slate-50",
  danger: "border border-red-600 bg-red-600 text-white shadow-sm hover:bg-red-700",
  ghost: "border border-transparent text-slate-600 hover:bg-slate-100 hover:text-slate-900",
};

export function Button({
  children,
  className = "",
  disabled,
  isLoading,
  variant = "primary",
  ...props
}: ButtonProps) {
  return (
    <button
      aria-busy={isLoading ? "true" : undefined}
      className={`tcms-focus inline-flex min-h-10 items-center justify-center rounded-md px-4 py-2 text-sm font-semibold transition disabled:cursor-not-allowed disabled:border-slate-200 disabled:bg-slate-100 disabled:text-slate-400 disabled:shadow-none ${variants[variant]} ${className}`}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading ? "Please wait..." : children}
    </button>
  );
}

