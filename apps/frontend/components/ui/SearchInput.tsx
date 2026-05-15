"use client";

import type { InputHTMLAttributes } from "react";

export function SearchInput(props: InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      className="w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-[#0948B3] focus:ring-2 focus:ring-blue-100 sm:max-w-xs"
      type="search"
      {...props}
    />
  );
}

