import React from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import PaymentsPage from "@/app/dashboard/billing/payments/page";
import { useAuth } from "@/hooks/useAuth";
import { listStudentPayments } from "@/lib/billing";

vi.mock("@/lib/billing", () => ({
  listStudentPayments: vi.fn(),
}));

vi.mock("@/hooks/useAuth", () => ({
  useAuth: vi.fn(),
}));

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <PaymentsPage />
    </QueryClientProvider>,
  );
}

describe("PaymentsPage", () => {
  beforeEach(() => {
    vi.mocked(listStudentPayments).mockReset();
    vi.mocked(useAuth).mockReturnValue({
      branchAssignments: [],
      error: null,
      hasPermission: vi.fn(() => false),
      hasRole: vi.fn(() => false),
      isAuthenticated: true,
      isLoading: false,
      login: vi.fn(),
      logout: vi.fn(),
      permissions: [],
      refreshSession: vi.fn(),
      user: null,
    });
  });

  it("renders loading state", () => {
    vi.mocked(listStudentPayments).mockReturnValue(new Promise(() => undefined));
    renderPage();

    expect(screen.getByRole("status")).toHaveTextContent("Loading payments...");
  });

  it("renders empty state", async () => {
    vi.mocked(listStudentPayments).mockResolvedValue({
      data: [],
      pagination: { count: 0, page: 1, page_size: 25, next: null, previous: null },
    });
    renderPage();

    expect(await screen.findByText("No payments found")).toBeInTheDocument();
  });

  it("renders data state", async () => {
    vi.mocked(listStudentPayments).mockResolvedValue({
      data: [
        {
          id: "payment-1",
          organization: "org-1",
          branch: "branch-1",
          academic_year: "year-1",
          student: "student-1",
          receipt_number: "RCPT-001",
          draft_receipt_number: null,
          payment_date_ad: "2026-04-15",
          payment_date_bs: "",
          payment_method: "cash",
          amount: "5000.00",
          discount_amount: "0.00",
          fine_amount: "0.00",
          net_received_amount: "5000.00",
          reference_number: "",
          file_path: "",
          is_advance_payment: false,
          status: "posted",
          created_by: null,
          approved_by: null,
          approved_at: null,
          posted_at: "2026-04-15T00:00:00Z",
          voided_by: null,
          voided_at: null,
          void_reason: "",
          notes: "",
          created_at: "2026-01-01T00:00:00Z",
          updated_at: "2026-01-01T00:00:00Z",
        },
      ],
      pagination: { count: 1, page: 1, page_size: 25, next: null, previous: null },
    });
    renderPage();

    expect(await screen.findByRole("link", { name: "RCPT-001" })).toHaveAttribute(
      "href",
      "/dashboard/billing/payments/payment-1",
    );
    expect(screen.getByText("Posted")).toBeInTheDocument();
  });

  it("shows new payment action for receptionist", async () => {
    vi.mocked(useAuth).mockReturnValue({
      branchAssignments: [],
      error: null,
      hasPermission: vi.fn(() => false),
      hasRole: vi.fn((role) => role === "receptionist"),
      isAuthenticated: true,
      isLoading: false,
      login: vi.fn(),
      logout: vi.fn(),
      permissions: [],
      refreshSession: vi.fn(),
      user: null,
    });
    vi.mocked(listStudentPayments).mockResolvedValue({
      data: [],
      pagination: { count: 0, page: 1, page_size: 25, next: null, previous: null },
    });

    renderPage();

    expect(await screen.findByRole("link", { name: /new payment/i })).toHaveAttribute(
      "href",
      "/dashboard/billing/payments/new",
    );
  });

  it("hides mutation action for teacher", async () => {
    vi.mocked(useAuth).mockReturnValue({
      branchAssignments: [],
      error: null,
      hasPermission: vi.fn(() => false),
      hasRole: vi.fn((role) => role === "teacher"),
      isAuthenticated: true,
      isLoading: false,
      login: vi.fn(),
      logout: vi.fn(),
      permissions: [],
      refreshSession: vi.fn(),
      user: null,
    });
    vi.mocked(listStudentPayments).mockResolvedValue({
      data: [],
      pagination: { count: 0, page: 1, page_size: 25, next: null, previous: null },
    });

    renderPage();

    expect(await screen.findByText("No payments found")).toBeInTheDocument();
    expect(screen.queryByRole("link", { name: /new payment/i })).not.toBeInTheDocument();
  });
});
