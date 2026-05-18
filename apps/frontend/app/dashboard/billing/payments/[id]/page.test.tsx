import React from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import PaymentDetailPage from "@/app/dashboard/billing/payments/[id]/page";
import { useAuth } from "@/hooks/useAuth";
import { approveStudentPayment, getStudentPayment } from "@/lib/billing";
import type { StudentPayment } from "@/types/billing";

vi.mock("@/hooks/useAuth", () => ({
  useAuth: vi.fn(),
}));

vi.mock("@/lib/billing", () => ({
  approveStudentPayment: vi.fn(),
  getStudentPayment: vi.fn(),
}));

const draftPayment: StudentPayment = {
  id: "payment-1",
  organization: "org-1",
  branch: "branch-1",
  academic_year: "year-1",
  student: "student-1",
  receipt_number: null,
  draft_receipt_number: "DR-000001",
  payment_date_ad: "2026-04-15",
  payment_date_bs: "",
  payment_method: "cash",
  amount: "500.00",
  discount_amount: "0.00",
  fine_amount: "0.00",
  net_received_amount: "500.00",
  reference_number: "",
  file_path: "",
  is_advance_payment: false,
  status: "draft",
  created_by: null,
  approved_by: null,
  approved_at: null,
  posted_at: null,
  voided_by: null,
  voided_at: null,
  void_reason: "",
  notes: "",
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-01T00:00:00Z",
};

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <PaymentDetailPage params={Promise.resolve({ id: "payment-1" })} />
    </QueryClientProvider>,
  );
}

function mockAuth(role: string) {
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

describe("PaymentDetailPage", () => {
  beforeEach(() => {
    vi.mocked(getStudentPayment).mockReset();
    vi.mocked(approveStudentPayment).mockReset();
    mockAuth("receptionist");
  });

  it("hides approve action for receptionist", async () => {
    vi.mocked(getStudentPayment).mockResolvedValue(draftPayment);

    renderPage();

    expect(await screen.findByRole("heading", { name: "DR-000001", level: 1 })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /approve and post/i })).not.toBeInTheDocument();
  });

  it("shows approve action for accountant", async () => {
    mockAuth("accountant");
    vi.mocked(getStudentPayment).mockResolvedValue(draftPayment);

    renderPage();

    expect(await screen.findByRole("button", { name: /approve and post/i })).toBeInTheDocument();
  });

  it("shows posted payment as read-only", async () => {
    mockAuth("accountant");
    vi.mocked(getStudentPayment).mockResolvedValue({ ...draftPayment, receipt_number: "RC-000001", status: "posted" });

    renderPage();

    expect(await screen.findByText(/This payment is posted and is read-only/i)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /approve and post/i })).not.toBeInTheDocument();
  });

  it("approves payment and refreshes detail", async () => {
    mockAuth("accountant");
    vi.mocked(getStudentPayment).mockResolvedValue(draftPayment);
    vi.mocked(approveStudentPayment).mockResolvedValue({ ...draftPayment, receipt_number: "RC-000001", status: "posted" });

    renderPage();

    fireEvent.click(await screen.findByRole("button", { name: /approve and post/i }));

    await waitFor(() => expect(approveStudentPayment).toHaveBeenCalledWith("payment-1"));
    expect(await screen.findByText("Payment approved and posted.")).toBeInTheDocument();
  });
});
