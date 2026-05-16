import React from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import StudentRefundsPage from "@/app/dashboard/billing/refunds/page";
import { useAuth } from "@/hooks/useAuth";
import { approveStudentRefund, listStudentRefunds, payStudentRefund } from "@/lib/billing";
import type { StudentRefund } from "@/types/billing";

vi.mock("@/lib/billing", () => ({
  approveStudentRefund: vi.fn(),
  listStudentRefunds: vi.fn(),
  payStudentRefund: vi.fn(),
}));

vi.mock("@/hooks/useAuth", () => ({
  useAuth: vi.fn(),
}));

const refund = (status: StudentRefund["status"]): StudentRefund => ({
  id: `refund-${status}`,
  organization: "org-1",
  branch: "branch-1",
  academic_year: "year-1",
  student: "student-1",
  original_payment: "payment-1",
  refund_voucher_number: "RF-001",
  refund_date_ad: "2026-04-15",
  refund_date_bs: "",
  refund_amount: "500.00",
  refund_reason: "Advance refund",
  status,
  requested_by: null,
  approved_by: null,
  approved_at: null,
  paid_by: null,
  paid_at: null,
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
      <StudentRefundsPage />
    </QueryClientProvider>,
  );
}

describe("StudentRefundsPage", () => {
  beforeEach(() => {
    vi.mocked(approveStudentRefund).mockReset();
    vi.mocked(listStudentRefunds).mockReset();
    vi.mocked(payStudentRefund).mockReset();
    mockRole("accountant");
  });

  it("shows approve action for financial approver", async () => {
    vi.mocked(listStudentRefunds).mockResolvedValue({
      data: [refund("pending_approval")],
      pagination: { count: 1, page: 1, page_size: 25, next: null, previous: null },
    });

    renderPage();

    expect(await screen.findByRole("button", { name: /approve refund/i })).toBeInTheDocument();
  });

  it("hides approve and pay actions for receptionist", async () => {
    vi.mocked(listStudentRefunds).mockResolvedValue({
      data: [refund("approved")],
      pagination: { count: 1, page: 1, page_size: 25, next: null, previous: null },
    });
    mockRole("receptionist");

    renderPage();

    expect(await screen.findByText("Read-only")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /approve refund/i })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /pay refund/i })).not.toBeInTheDocument();
  });

  it("hides approve and pay actions for auditor", async () => {
    vi.mocked(listStudentRefunds).mockResolvedValue({
      data: [refund("approved")],
      pagination: { count: 1, page: 1, page_size: 25, next: null, previous: null },
    });
    mockRole("auditor");

    renderPage();

    expect(await screen.findByText("Read-only")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /approve refund/i })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /pay refund/i })).not.toBeInTheDocument();
  });

  it("does not show mutation action for paid records", async () => {
    vi.mocked(listStudentRefunds).mockResolvedValue({
      data: [refund("paid")],
      pagination: { count: 1, page: 1, page_size: 25, next: null, previous: null },
    });

    renderPage();

    expect(await screen.findByText("Read-only")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /pay refund/i })).not.toBeInTheDocument();
  });

  it("calls pay refund action", async () => {
    vi.mocked(listStudentRefunds).mockResolvedValue({
      data: [refund("approved")],
      pagination: { count: 1, page: 1, page_size: 25, next: null, previous: null },
    });
    vi.mocked(payStudentRefund).mockResolvedValue(refund("paid"));

    renderPage();
    fireEvent.click(await screen.findByRole("button", { name: /pay refund/i }));

    await waitFor(() => expect(payStudentRefund).toHaveBeenCalled());
    expect(vi.mocked(payStudentRefund).mock.calls[0][0]).toBe("refund-approved");
  });
});
