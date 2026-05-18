import type { ReactNode } from "react";

export interface SimpleTableColumn<T> {
  header: string;
  render: (row: T) => ReactNode;
}

interface SimpleTableProps<T> {
  "aria-label"?: string;
  columns: SimpleTableColumn<T>[];
  emptyMessage?: string;
  emptyTitle?: string;
  getRowKey: (row: T) => string;
  rows: T[];
}

export function SimpleTable<T>({
  "aria-label": ariaLabel = "Data table",
  columns,
  emptyMessage = "No records match the current view.",
  emptyTitle = "No records found",
  getRowKey,
  rows,
}: SimpleTableProps<T>) {
  return (
    <div className="tcms-card overflow-hidden">
      <div className="overflow-x-auto">
        <table aria-label={ariaLabel} className="min-w-[720px] divide-y divide-slate-200 text-left text-sm sm:min-w-full">
          <thead className="bg-slate-50/90 text-xs font-bold uppercase tracking-wide text-slate-500">
            <tr>
              {columns.map((column) => (
                <th className="whitespace-nowrap px-4 py-3.5" key={column.header} scope="col">
                  {column.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 bg-white">
            {rows.length === 0 ? (
              <tr>
                <td className="px-4 py-10 text-center" colSpan={columns.length}>
                  <p className="text-sm font-semibold text-[#262B40]">{emptyTitle}</p>
                  <p className="mt-1 text-sm text-slate-500">{emptyMessage}</p>
                </td>
              </tr>
            ) : (
              rows.map((row) => (
                <tr className="transition hover:bg-[#F0F3FF]" key={getRowKey(row)}>
                  {columns.map((column) => (
                    <td className="whitespace-nowrap px-4 py-3.5 align-middle text-slate-700" key={column.header}>
                      {column.render(row)}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

