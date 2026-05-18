"use client";

import type { InputHTMLAttributes } from "react";

export function SearchInput(props: InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      className="tcms-control w-full bg-white px-3 py-2 text-sm sm:max-w-xs"
      type="search"
      {...props}
    />
  );
}

