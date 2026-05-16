import React from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import BillingDiscountsPage from "@/app/dashboard/billing/discounts/page";
import { useAuth } from "@/hooks/useAuth";
import { approveBillingDiscount, listBillingDiscounts } from "@/lib/billing";
import type { BillingDiscount } from "@/types/billing";

vi.mock("@/lib/billing", () => ({
  approveBillingDiscount: vi.fn(),
  listBillingDiscounts: vi.fn(),
}));

vi.mock("@/hooks/useAuth", () => ({
  useAuth: vi.fn(),
}));

const discount = (status: BillingDiscount["status"]): BillingDiscount => ({
  id: `discount-${status}`,
  organization: "org-1",
  branch: "branch-1",
  academic_year: "year-1",
  student: "student-1",
  class_enrollment: null,
  fee_due: "due-1",
  invoice: null,
  discount_type: "scholarship",
  discount_percentage: null,
  discount_amount: "500.00",
  reason: "Scholarship",
  status,
  approved_by: null,
  approved_at: null,
  notes: "",
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-01T00:00:00Z",
});

function mockRole(role: string) {
  vi.mocked(useAuth).mockReturnValue({
    branchAssignments: [],
    error: null,
    hasPermission: vi.fn(() => false),
    hasRole: vi.fn((candidate) => candidate === role),
    isAuthenticated: true,
    isLoading: false,
    login: vi.fn(),
    logout: vi.fn(),
    permissions: [],
    refreshSession: vi.fn(),
    user: null,
  });
}

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <BillingDiscountsPage />
    </QueryClientProvider>,
  );
}

describe("BillingDiscountsPage", () => {
  beforeEach(() => {
    vi.mocked(approveBillingDiscount).mockReset();
    vi.mocked(listBillingDiscounts).mockReset();
    mockRole("accountant");
  });

  it("shows approve action for financial approver", async () => {
    vi.mocked(listBillingDiscounts).mockResolvedValue({
      data: [discount("pending_approval")],
      pagination: { count: 1, page: 1, page_size: 25, next: null, previous: null },
    });

    renderPage();

    expect(await screen.findByRole("button", { name: /approve discount/i })).toBeInTheDocument();
  });

  it("hides approve action for receptionist", async () => {
    vi.mocked(listBillingDiscounts).mockResolvedValue({
      data: [discount("pending_approval")],
      pagination: { count: 1, page: 1, page_size: 25, next: null, previous: null },
    });
    mockRole("receptionist");
    renderPage();

    expect(await screen.findByText("Read-only")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /approve discount/i })).not.toBeInTheDocument();
  });

  it("hides approve action for auditor", async () => {
    vi.mocked(listBillingDiscounts).mockResolvedValue({
      data: [discount("pending_approval")],
      pagination: { count: 1, page: 1, page_size: 25, next: null, previous: null },
    });
    mockRole("auditor");
    renderPage();

    expect(await screen.findByText("Read-only")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /approve discount/i })).not.toBeInTheDocument();
  });

  it("does not show mutation action for approved records", async () => {
    vi.mocked(listBillingDiscounts).mockResolvedValue({
      data: [discount("approved")],
      pagination: { count: 1, page: 1, page_size: 25, next: null, previous: null },
    });

    renderPage();

    expect(await screen.findByText("Read-only")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /approve discount/i })).not.toBeInTheDocument();
  });

  it("calls approve discount action", async () => {
    vi.mocked(listBillingDiscounts).mockResolvedValue({
      data: [discount("pending_approval")],
      pagination: { count: 1, page: 1, page_size: 25, next: null, previous: null },
    });
    vi.mocked(approveBillingDiscount).mockResolvedValue(discount("approved"));

    renderPage();
    fireEvent.click(await screen.findByRole("button", { name: /approve discount/i }));

    await waitFor(() => expect(approveBillingDiscount).toHaveBeenCalled());
    expect(vi.mocked(approveBillingDiscount).mock.calls[0][0]).toBe("discount-pending_approval");
  });
});
