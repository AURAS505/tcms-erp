import { afterEach, describe, expect, it, vi } from "vitest";
import { clearCsrfTokenCache } from "@/lib/api-client";
import {
  approveTeacherEarning,
  approveTeacherPayment,
  createDraftTeacherPayment,
  createManualTeacherEarning,
  getTeacherEarning,
  getTeacherPayment,
  getTeacherPaymentBatch,
  listTeacherDeductions,
  listTeacherEarnings,
  listTeacherPaymentAllocations,
  listTeacherPaymentBatches,
  listTeacherPayments,
  postTeacherEarning,
  postTeacherPayment,
  voidTeacherPaymentPlaceholder,
} from "@/lib/payroll";

const mockFetch = (data: unknown) => {
  const fetchMock = vi.fn((url: string, _init?: RequestInit) => Promise.resolve({
    ok: true,
    status: 200,
    json: vi.fn().mockResolvedValue({
      success: true,
      data: url.endsWith("/api/v1/auth/csrf/") ? { csrf_token: "csrf-token-1" } : data,
      errors: null,
      meta: {
        pagination: {
          count: Array.isArray(data) ? data.length : 1,
          page: 1,
          page_size: 25,
          next: null,
          previous: null,
        },
      },
    }),
  }));
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
};

describe("payroll API client", () => {
  afterEach(() => {
    clearCsrfTokenCache();
    vi.unstubAllGlobals();
  });

  it("calls expected payroll primary endpoints", async () => {
    const fetchMock = mockFetch([]);

    await listTeacherEarnings("math");
    await getTeacherEarning("earning-1");
    await listTeacherPaymentBatches();
    await getTeacherPaymentBatch("batch-1");
    await listTeacherPayments("TPV");
    await getTeacherPayment("payment-1");

    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      "http://localhost:8000/api/v1/teacher-earnings/?search=math",
      expect.objectContaining({ credentials: "include" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      "http://localhost:8000/api/v1/teacher-earnings/earning-1/",
      expect.objectContaining({ credentials: "include" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      3,
      "http://localhost:8000/api/v1/teacher-payment-batches/",
      expect.objectContaining({ credentials: "include" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      4,
      "http://localhost:8000/api/v1/teacher-payment-batches/batch-1/",
      expect.objectContaining({ credentials: "include" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      5,
      "http://localhost:8000/api/v1/teacher-payments/?search=TPV",
      expect.objectContaining({ credentials: "include" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      6,
      "http://localhost:8000/api/v1/teacher-payments/payment-1/",
      expect.objectContaining({ credentials: "include" }),
    );
  });

  it("calls expected payroll supporting endpoints", async () => {
    const fetchMock = mockFetch([]);

    await listTeacherPaymentAllocations();
    await listTeacherDeductions();

    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      "http://localhost:8000/api/v1/teacher-payment-allocations/",
      expect.objectContaining({ credentials: "include" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      "http://localhost:8000/api/v1/teacher-deductions/",
      expect.objectContaining({ credentials: "include" }),
    );
  });

  it("sends teacher earning filter query params", async () => {
    const fetchMock = mockFetch([]);

    await listTeacherEarnings({
      organization: "org-1",
      branch: "branch-1",
      academic_year: "year-1",
      teacher: "teacher-1",
      open_only: true,
    });

    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/api/v1/teacher-earnings/?organization=org-1&branch=branch-1&academic_year=year-1&teacher=teacher-1&open_only=true",
      expect.objectContaining({ credentials: "include" }),
    );
  });

  it("calls expected payroll mutation endpoints", async () => {
    const fetchMock = mockFetch({ id: "record-1" });

    await createManualTeacherEarning({
      organization: "org-1",
      branch: "branch-1",
      academic_year: "year-1",
      teacher: "teacher-1",
      earning_date_ad: "2026-04-15",
      gross_amount: "1000.00",
    });
    await approveTeacherEarning("earning-1");
    await postTeacherEarning("earning-1");
    await createDraftTeacherPayment({
      organization: "org-1",
      branch: "branch-1",
      academic_year: "year-1",
      teacher: "teacher-1",
      payment_date_ad: "2026-04-16",
      payment_method: "cash",
      amount: "750.00",
      allocations: [
        { teacher_earning: "earning-1", amount_allocated: "500.00" },
        { teacher_earning: "earning-2", amount_allocated: "250.00" },
      ],
    });
    await approveTeacherPayment("payment-1");
    await postTeacherPayment("payment-1");
    await voidTeacherPaymentPlaceholder("payment-1", { reason: "Duplicate draft" });

    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/api/v1/teacher-earnings/create-manual/",
      expect.objectContaining({ method: "POST", headers: expect.any(Headers), body: expect.stringContaining('"gross_amount":"1000.00"') }),
    );
    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/api/v1/teacher-earnings/earning-1/approve/",
      expect.objectContaining({ method: "POST", body: "{}" }),
    );
    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/api/v1/teacher-earnings/earning-1/post/",
      expect.objectContaining({ method: "POST", body: "{}" }),
    );
    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/api/v1/teacher-payments/create-draft/",
      expect.objectContaining({ method: "POST", body: expect.stringContaining('"teacher_earning":"earning-2"') }),
    );
    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/api/v1/teacher-payments/payment-1/approve/",
      expect.objectContaining({ method: "POST", body: "{}" }),
    );
    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/api/v1/teacher-payments/payment-1/post/",
      expect.objectContaining({ method: "POST", body: "{}" }),
    );
    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/api/v1/teacher-payments/payment-1/void-placeholder/",
      expect.objectContaining({ method: "POST", body: expect.stringContaining("Duplicate draft") }),
    );
    const earningCall = fetchMock.mock.calls.find(([url]) => url === "http://localhost:8000/api/v1/teacher-earnings/create-manual/");
    expect(earningCall).toBeDefined();
    const earningHeaders = earningCall?.[1]?.headers as Headers;
    expect(earningHeaders.get("X-CSRFToken")).toBe("csrf-token-1");
  });
});
