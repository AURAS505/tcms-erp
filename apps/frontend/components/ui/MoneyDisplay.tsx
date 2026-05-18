export function MoneyDisplay({ amount }: { amount?: string | number | null }) {
  if (amount === null || amount === undefined || amount === "") {
    return <span className="text-slate-400">Not set</span>;
  }

  const numericAmount = typeof amount === "number" ? amount : Number(amount);

  if (!Number.isFinite(numericAmount)) {
    return <span className="font-medium tabular-nums text-slate-700">{amount}</span>;
  }

  return (
    <span className={`font-semibold tabular-nums ${numericAmount < 0 ? "text-red-700" : "text-slate-800"}`}>
      {numericAmount.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
    </span>
  );
}
