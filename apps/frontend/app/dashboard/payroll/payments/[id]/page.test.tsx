import React from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import TeacherPaymentDetailPage from "@/app/dashboard/payroll/payments/[id]/page";
import { useAuth } from "@/hooks/useAuth";
import { approveTeacherPayment, getTeacherPayment, postTeacherPayment } from "@/lib/payroll";
import type { TeacherPayment } from "@/types/payroll";

vi.mock("@/hooks/useAuth", () => ({
  useAuth: vi.fn(),
}));

vi.mock("@/lib/payroll", () => ({
  approveTeacherPayment: vi.fn(),
  getTeacherPayment: vi.fn(),
  postTeacherPayment: vi.fn(),
}));

const payment = (status: TeacherPayment["status"]): TeacherPayment => ({
  id: "payment-1",
  organization: "org-1",
  branch: "branch-1",
  academic_year: "year-1",
  academic_period: null,
  payment_batch: null,
  teacher: "teacher-1",
  voucher_number: status === "posted" ? "TV-000001" : null,
  draft_voucher_number: "TDV-000001",
  payment_date_ad: "2026-04-15",
  payment_date_bs: "",
  payment_method: "cash",
  amount: "500.00",
  deduction_amount: "0.00",
  net_paid_amount: "500.00",
  reference_number: "",
  acknowledgement_file_path: "",
  status,
  created_by: null,
  approved_by: null,
  approved_at: null,
  posted_at: status === "posted" ? "2026-04-15T00:00:00Z" : null,
  voided_by: null,
  voided_at: null,
  void_reason: "",
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
      <TeacherPaymentDetailPage params={{ id: "payment-1" }} />
    </QueryClientProvider>,
  );
}

describe("TeacherPaymentDetailPage", () => {
  beforeEach(() => {
    vi.mocked(approveTeacherPayment).mockReset();
    vi.mocked(getTeacherPayment).mockReset();
    vi.mocked(postTeacherPayment).mockReset();
    mockRole("accountant");
  });

  it("shows approve action for financial approver", async () => {
    vi.mocked(getTeacherPayment).mockResolvedValue(payment("draft"));

    renderPage();

    expect(await screen.findByRole("button", { name: /approve and post/i })).toBeInTheDocument();
  });

  it("shows post action for approved payment", async () => {
    vi.mocked(getTeacherPayment).mockResolvedValue(payment("approved"));

    renderPage();

    expect(await screen.findByRole("button", { name: /post payment/i })).toBeInTheDocument();
  });

  it("hides mutation actions for teacher", async () => {
    mockRole("teacher");
    vi.mocked(getTeacherPayment).mockResolvedValue(payment("draft"));

    renderPage();

    expect(await screen.findByRole("heading", { name: "TDV-000001", level: 1 })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /approve and post/i })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /post payment/i })).not.toBeInTheDocument();
  });

  it("shows posted payment as read-only", async () => {
    vi.mocked(getTeacherPayment).mockResolvedValue(payment("posted"));

    renderPage();

    expect(await screen.findByText(/This teacher payment is posted and is read-only/i)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /approve and post/i })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /post payment/i })).not.toBeInTheDocument();
  });

  it("approves payment through payroll API helper", async () => {
    vi.mocked(getTeacherPayment).mockResolvedValue(payment("draft"));
    vi.mocked(approveTeacherPayment).mockResolvedValue(payment("posted"));

    renderPage();
    fireEvent.click(await screen.findByRole("button", { name: /approve and post/i }));

    await waitFor(() => expect(approveTeacherPayment).toHaveBeenCalledWith("payment-1"));
    expect(await screen.findByText("Teacher payment approved and posted.")).toBeInTheDocument();
  });

  it("posts payment through payroll API helper", async () => {
    vi.mocked(getTeacherPayment).mockResolvedValue(payment("approved"));
    vi.mocked(postTeacherPayment).mockResolvedValue(payment("posted"));

    renderPage();
    fireEvent.click(await screen.findByRole("button", { name: /post payment/i }));

    await waitFor(() => expect(postTeacherPayment).toHaveBeenCalledWith("payment-1"));
    expect(await screen.findByText("Teacher payment posted.")).toBeInTheDocument();
  });
});
