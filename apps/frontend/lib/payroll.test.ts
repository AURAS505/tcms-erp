import { afterEach, describe, expect, it, vi } from "vitest";
import {
  getTeacherEarning,
  getTeacherPayment,
  getTeacherPaymentBatch,
  listTeacherDeductions,
  listTeacherEarnings,
  listTeacherPaymentAllocations,
  listTeacherPaymentBatches,
  listTeacherPayments,
} from "@/lib/payroll";

const mockFetch = (data: unknown) => {
  const fetchMock = vi.fn().mockResolvedValue({
    ok: true,
    status: 200,
    json: vi.fn().mockResolvedValue({
      success: true,
      data,
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
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
};

describe("payroll API client", () => {
  afterEach(() => {
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
});
