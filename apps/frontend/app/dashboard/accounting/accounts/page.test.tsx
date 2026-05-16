import React from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import AccountsPage from "@/app/dashboard/accounting/accounts/page";
import { listAccounts } from "@/lib/accounting";

vi.mock("@/lib/accounting", () => ({
  listAccounts: vi.fn(),
}));

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <AccountsPage />
    </QueryClientProvider>,
  );
}

describe("AccountsPage", () => {
  beforeEach(() => {
    vi.mocked(listAccounts).mockReset();
  });

  it("renders loading state", () => {
    vi.mocked(listAccounts).mockReturnValue(new Promise(() => undefined));
    renderPage();

    expect(screen.getByRole("status")).toHaveTextContent("Loading accounts...");
  });

  it("renders empty state", async () => {
    vi.mocked(listAccounts).mockResolvedValue({
      data: [],
      pagination: { count: 0, page: 1, page_size: 25, next: null, previous: null },
    });
    renderPage();

    expect(await screen.findByText("No accounts found")).toBeInTheDocument();
  });

  it("renders data state", async () => {
    vi.mocked(listAccounts).mockResolvedValue({
      data: [
        {
          id: "account-1",
          organization: "org-1",
          code: "1110",
          name: "Cash",
          account_type: "asset",
          parent: null,
          normal_balance: "debit",
          is_system_account: true,
          is_active: true,
          description: "",
          created_at: "2026-01-01T00:00:00Z",
          updated_at: "2026-01-01T00:00:00Z",
        },
      ],
      pagination: { count: 1, page: 1, page_size: 25, next: null, previous: null },
    });
    renderPage();

    expect(await screen.findByRole("link", { name: "1110" })).toHaveAttribute(
      "href",
      "/dashboard/accounting/accounts/account-1",
    );
    expect(screen.getByText("Cash")).toBeInTheDocument();
  });
});
