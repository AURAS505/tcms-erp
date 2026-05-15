import React from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import InvoicesPage from "@/app/dashboard/billing/invoices/page";
import { listInvoices } from "@/lib/billing";

vi.mock("@/lib/billing", () => ({
  listInvoices: vi.fn(),
}));

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <InvoicesPage />
    </QueryClientProvider>,
  );
}

describe("InvoicesPage", () => {
  beforeEach(() => {
    vi.mocked(listInvoices).mockReset();
  });

  it("renders loading state", () => {
    vi.mocked(listInvoices).mockReturnValue(new Promise(() => undefined));
    renderPage();

    expect(screen.getByRole("status")).toHaveTextContent("Loading invoices...");
  });

  it("renders empty state", async () => {
    vi.mocked(listInvoices).mockResolvedValue({
      data: [],
      pagination: { count: 0, page: 1, page_size: 25, next: null, previous: null },
    });
    renderPage();

    expect(await screen.findByText("No invoices found")).toBeInTheDocument();
  });

  it("renders data state", async () => {
    vi.mocked(listInvoices).mockResolvedValue({
      data: [
        {
          id: "invoice-1",
          organization: "org-1",
          branch: "branch-1",
          academic_year: "year-1",
          academic_period: null,
          student: "student-1",
          invoice_number: "INV-001",
          invoice_date_ad: "2026-04-15",
          invoice_date_bs: "",
          due_date_ad: "2026-04-20",
          due_date_bs: "",
          subtotal: "5000.00",
          discount_amount: "0.00",
          fine_amount: "0.00",
          total_amount: "5000.00",
          paid_amount: "0.00",
          balance_amount: "5000.00",
          status: "unpaid",
          notes: "",
          created_at: "2026-01-01T00:00:00Z",
          updated_at: "2026-01-01T00:00:00Z",
        },
      ],
      pagination: { count: 1, page: 1, page_size: 25, next: null, previous: null },
    });
    renderPage();

    expect(await screen.findByRole("link", { name: "INV-001" })).toHaveAttribute(
      "href",
      "/dashboard/billing/invoices/invoice-1",
    );
    expect(screen.getByText("Unpaid")).toBeInTheDocument();
  });
});
