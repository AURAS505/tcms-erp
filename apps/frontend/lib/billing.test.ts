import { afterEach, describe, expect, it, vi } from "vitest";
import {
  getFeeDue,
  getFeePlan,
  getInvoice,
  getStudentPayment,
  approveStudentPayment,
  createDraftStudentPayment,
  listAdvanceBalances,
  listBillingDiscounts,
  listBillingFines,
  listBillingWaivers,
  listFeeDues,
  listFeePlans,
  listInvoices,
  listStudentPayments,
  listStudentRefunds,
} from "@/lib/billing";

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

describe("billing API client", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("calls expected main billing endpoints", async () => {
    const fetchMock = mockFetch([]);

    await listFeePlans("monthly");
    await getFeePlan("plan-1");
    await listFeeDues();
    await getFeeDue("due-1");
    await listInvoices("INV");
    await getInvoice("invoice-1");
    await listStudentPayments();
    await getStudentPayment("payment-1");

    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      "http://localhost:8000/api/v1/fee-plans/?search=monthly",
      expect.objectContaining({ credentials: "include" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      "http://localhost:8000/api/v1/fee-plans/plan-1/",
      expect.objectContaining({ credentials: "include" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      3,
      "http://localhost:8000/api/v1/student-fee-dues/",
      expect.objectContaining({ credentials: "include" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      4,
      "http://localhost:8000/api/v1/student-fee-dues/due-1/",
      expect.objectContaining({ credentials: "include" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      5,
      "http://localhost:8000/api/v1/student-invoices/?search=INV",
      expect.objectContaining({ credentials: "include" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      6,
      "http://localhost:8000/api/v1/student-invoices/invoice-1/",
      expect.objectContaining({ credentials: "include" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      7,
      "http://localhost:8000/api/v1/student-payments/",
      expect.objectContaining({ credentials: "include" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      8,
      "http://localhost:8000/api/v1/student-payments/payment-1/",
      expect.objectContaining({ credentials: "include" }),
    );
  });

  it("calls expected supporting billing endpoints", async () => {
    const fetchMock = mockFetch([]);

    await listAdvanceBalances();
    await listBillingDiscounts();
    await listBillingWaivers();
    await listBillingFines();
    await listStudentRefunds();

    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      "http://localhost:8000/api/v1/student-advance-balances/",
      expect.objectContaining({ credentials: "include" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      "http://localhost:8000/api/v1/billing-discounts/",
      expect.objectContaining({ credentials: "include" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      3,
      "http://localhost:8000/api/v1/billing-waivers/",
      expect.objectContaining({ credentials: "include" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      4,
      "http://localhost:8000/api/v1/billing-fines/",
      expect.objectContaining({ credentials: "include" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      5,
      "http://localhost:8000/api/v1/student-refunds/",
      expect.objectContaining({ credentials: "include" }),
    );
  });

  it("calls expected student payment workflow endpoints", async () => {
    const fetchMock = mockFetch({ id: "payment-1" });

    await createDraftStudentPayment({
      organization: "org-1",
      branch: "branch-1",
      academic_year: "year-1",
      student: "student-1",
      payment_date_ad: "2026-04-15",
      payment_method: "cash",
      amount: "500.00",
      is_advance_payment: true,
    });
    await approveStudentPayment("payment-1");

    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      "http://localhost:8000/api/v1/student-payments/create-draft/",
      expect.objectContaining({ body: expect.any(String), credentials: "include", method: "POST" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      "http://localhost:8000/api/v1/student-payments/payment-1/approve/",
      expect.objectContaining({ body: "{}", credentials: "include", method: "POST" }),
    );
  });
});
