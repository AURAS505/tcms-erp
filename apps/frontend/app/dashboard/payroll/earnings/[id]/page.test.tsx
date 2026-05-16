import React from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import TeacherEarningDetailPage from "@/app/dashboard/payroll/earnings/[id]/page";
import { useAuth } from "@/hooks/useAuth";
import { approveTeacherEarning, getTeacherEarning, postTeacherEarning } from "@/lib/payroll";
import type { TeacherEarning } from "@/types/payroll";

vi.mock("@/hooks/useAuth", () => ({
  useAuth: vi.fn(),
}));

vi.mock("@/lib/payroll", () => ({
  approveTeacherEarning: vi.fn(),
  getTeacherEarning: vi.fn(),
  postTeacherEarning: vi.fn(),
}));

const earning = (status: TeacherEarning["status"]): TeacherEarning => ({
  id: "earning-1",
  organization: "org-1",
  branch: "branch-1",
  academic_year: "year-1",
  academic_period: null,
  teacher: "teacher-1",
  student: null,
  class_room: null,
  class_enrollment: null,
  student_payment: null,
  earning_source: "manual_adjustment",
  earning_date_ad: "2026-04-15",
  earning_date_bs: "",
  period_label: "Baishakh 2083",
  gross_amount: "1000.00",
  deduction_amount: "100.00",
  net_amount: "900.00",
  paid_amount: "0.00",
  balance_amount: "900.00",
  status,
  created_by: null,
  approved_by: null,
  approved_at: null,
  posted_at: status === "posted" ? "2026-04-15T00:00:00Z" : null,
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
      <TeacherEarningDetailPage params={{ id: "earning-1" }} />
    </QueryClientProvider>,
  );
}

describe("TeacherEarningDetailPage", () => {
  beforeEach(() => {
    vi.mocked(approveTeacherEarning).mockReset();
    vi.mocked(getTeacherEarning).mockReset();
    vi.mocked(postTeacherEarning).mockReset();
    mockRole("accountant");
  });

  it("shows approve action for financial approver", async () => {
    vi.mocked(getTeacherEarning).mockResolvedValue(earning("draft"));

    renderPage();

    expect(await screen.findByRole("button", { name: /approve earning/i })).toBeInTheDocument();
  });

  it("shows post action for approved earning", async () => {
    vi.mocked(getTeacherEarning).mockResolvedValue(earning("approved"));

    renderPage();

    expect(await screen.findByRole("button", { name: /post earning/i })).toBeInTheDocument();
  });

  it("hides mutation actions for receptionist", async () => {
    mockRole("receptionist");
    vi.mocked(getTeacherEarning).mockResolvedValue(earning("draft"));

    renderPage();

    expect(await screen.findByRole("heading", { name: "Baishakh 2083", level: 1 })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /approve earning/i })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /post earning/i })).not.toBeInTheDocument();
  });

  it("shows posted earning as read-only", async () => {
    vi.mocked(getTeacherEarning).mockResolvedValue(earning("posted"));

    renderPage();

    expect(await screen.findByText(/This teacher earning is posted and is read-only/i)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /approve earning/i })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /post earning/i })).not.toBeInTheDocument();
  });

  it("approves earning through payroll API helper", async () => {
    vi.mocked(getTeacherEarning).mockResolvedValue(earning("draft"));
    vi.mocked(approveTeacherEarning).mockResolvedValue(earning("approved"));

    renderPage();
    fireEvent.click(await screen.findByRole("button", { name: /approve earning/i }));

    await waitFor(() => expect(approveTeacherEarning).toHaveBeenCalledWith("earning-1"));
    expect(await screen.findByText("Teacher earning approved.")).toBeInTheDocument();
  });

  it("posts earning through payroll API helper", async () => {
    vi.mocked(getTeacherEarning).mockResolvedValue(earning("approved"));
    vi.mocked(postTeacherEarning).mockResolvedValue(earning("posted"));

    renderPage();
    fireEvent.click(await screen.findByRole("button", { name: /post earning/i }));

    await waitFor(() => expect(postTeacherEarning).toHaveBeenCalledWith("earning-1"));
    expect(await screen.findByText("Teacher earning posted.")).toBeInTheDocument();
  });
});
