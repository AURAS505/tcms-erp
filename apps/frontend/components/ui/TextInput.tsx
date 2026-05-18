import type { InputHTMLAttributes } from "react";

interface TextInputProps extends InputHTMLAttributes<HTMLInputElement> {
  error?: string;
  helpText?: string;
  label: string;
}

export function TextInput({ error, helpText, id, label, className = "", ...props }: TextInputProps) {
  const inputId = id ?? props.name ?? label.toLowerCase().replace(/\s+/g, "-");
  const helpId = helpText ? `${inputId}-help` : undefined;
  const errorId = error ? `${inputId}-error` : undefined;

  return (
    <label className="block text-sm font-semibold text-slate-700" htmlFor={inputId}>
      <span>{label}</span>
      <input
        id={inputId}
        aria-describedby={[helpId, errorId].filter(Boolean).join(" ") || undefined}
        aria-invalid={error ? "true" : undefined}
        className={`tcms-control mt-2 block px-3 py-2.5 text-sm ${error ? "border-red-300 focus:border-red-500 focus:ring-red-100" : ""} ${className}`}
        {...props}
      />
      {helpText ? <span className="mt-1.5 block text-xs font-medium text-slate-500" id={helpId}>{helpText}</span> : null}
      {error ? <span className="mt-1.5 block text-xs font-semibold text-red-600" id={errorId}>{error}</span> : null}
    </label>
  );
}

