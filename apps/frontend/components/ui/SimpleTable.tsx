import type { ReactNode } from "react";

export interface SimpleTableColumn<T> {
  header: string;
  render: (row: T) => ReactNode;
}

interface SimpleTableProps<T> {
  columns: SimpleTableColumn<T>[];
  getRowKey: (row: T) => string;
  rows: T[];
}

export function SimpleTable<T>({ columns, getRowKey, rows }: SimpleTableProps<T>) {
  return (
    <div className="overflow-hidden rounded-lg bg-white shadow-[0_2px_18px_rgba(38,43,64,0.08)]">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-200 text-left text-sm">
          <thead className="bg-slate-50 text-xs font-semibold uppercase text-slate-500">
            <tr>
              {columns.map((column) => (
                <th className="px-4 py-3" key={column.header} scope="col">
                  {column.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {rows.map((row) => (
              <tr className="hover:bg-[#F0F3FF]" key={getRowKey(row)}>
                {columns.map((column) => (
                  <td className="px-4 py-3 align-middle text-slate-700" key={column.header}>
                    {column.render(row)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

