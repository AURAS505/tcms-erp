export function MoneyDisplay({ amount }: { amount?: string | number | null }) {
  if (amount === null || amount === undefined || amount === "") {
    return <span>Not set</span>;
  }

  const numericAmount = typeof amount === "number" ? amount : Number(amount);

  if (!Number.isFinite(numericAmount)) {
    return <span>{amount}</span>;
  }

  return <span>{numericAmount.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>;
}
