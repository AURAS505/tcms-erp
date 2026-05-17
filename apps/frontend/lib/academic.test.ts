import { afterEach, describe, expect, it, vi } from "vitest";
import { clearCsrfTokenCache } from "@/lib/api-client";
import {
  cancelAcademicRollover,
  executeAcademicRollover,
  getAcademicRollover,
  getAcademicRolloverSummary,
  getAcademicYear,
  hardCloseAcademicYear,
  listAcademicRollovers,
  listAcademicYears,
  prepareAcademicRollover,
  softCloseAcademicYear,
  validateAcademicRollover,
} from "@/lib/academic";

const mockFetch = (data: unknown) => {
  const fetchMock = vi.fn((url: string, _init?: RequestInit) => Promise.resolve({
    ok: true,
    status: 200,
    json: vi.fn().mockResolvedValue({
      success: true,
      data: url.endsWith("/api/v1/auth/csrf/") ? { csrf_token: "csrf-token-1" } : data,
      errors: null,
      meta: { pagination: { count: Array.isArray(data) ? data.length : 1, page: 1, page_size: 25, next: null, previous: null } },
    }),
  }));
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
};

describe("academic API client", () => {
  afterEach(() => {
    clearCsrfTokenCache();
    vi.unstubAllGlobals();
  });

  it("calls expected academic year and rollover endpoints", async () => {
    const fetchMock = mockFetch([]);

    await listAcademicYears("2083");
    await getAcademicYear("year-1");
    await listAcademicRollovers();
    await getAcademicRollover("rollover-1");
    await prepareAcademicRollover({ organization: "org-1", from_academic_year: "year-1", notes: "close year" });
    await validateAcademicRollover("rollover-1");
    await executeAcademicRollover("rollover-1", {
      hard_close: true,
      new_year_data: {
        name: "2084",
        bs_start_year: 2084,
        bs_end_year: 2085,
        bs_start_date: "2084-01-01",
        bs_end_date: "2084-12-30",
        ad_start_date: "2027-04-14",
        ad_end_date: "2028-04-13",
      },
    });
    await cancelAcademicRollover("rollover-1", { reason: "Not ready" });
    await getAcademicRolloverSummary("rollover-1");
    await softCloseAcademicYear("year-1", { reason: "Reviewed" });
    await hardCloseAcademicYear("year-1", { reason: "Final" });

    expect(fetchMock).toHaveBeenNthCalledWith(1, "http://localhost:8000/api/v1/academic-years/?search=2083", expect.objectContaining({ credentials: "include" }));
    expect(fetchMock).toHaveBeenNthCalledWith(2, "http://localhost:8000/api/v1/academic-years/year-1/", expect.objectContaining({ credentials: "include" }));
    expect(fetchMock).toHaveBeenNthCalledWith(3, "http://localhost:8000/api/v1/academic-year-rollovers/", expect.objectContaining({ credentials: "include" }));
    expect(fetchMock).toHaveBeenNthCalledWith(4, "http://localhost:8000/api/v1/academic-year-rollovers/rollover-1/", expect.objectContaining({ credentials: "include" }));
    expect(fetchMock).toHaveBeenCalledWith("http://localhost:8000/api/v1/academic-year-rollovers/prepare/", expect.objectContaining({ method: "POST", headers: expect.any(Headers), body: expect.stringContaining("close year") }));
    expect(fetchMock).toHaveBeenCalledWith("http://localhost:8000/api/v1/academic-year-rollovers/rollover-1/validate/", expect.objectContaining({ method: "POST", body: "{}" }));
    expect(fetchMock).toHaveBeenCalledWith("http://localhost:8000/api/v1/academic-year-rollovers/rollover-1/execute/", expect.objectContaining({ method: "POST", body: expect.stringContaining("2084") }));
    expect(fetchMock).toHaveBeenCalledWith("http://localhost:8000/api/v1/academic-year-rollovers/rollover-1/cancel/", expect.objectContaining({ method: "POST", body: expect.stringContaining("Not ready") }));
    expect(fetchMock).toHaveBeenCalledWith("http://localhost:8000/api/v1/academic-year-rollovers/rollover-1/summary/", expect.objectContaining({ credentials: "include" }));
    expect(fetchMock).toHaveBeenCalledWith("http://localhost:8000/api/v1/academic-years/year-1/soft-close/", expect.objectContaining({ method: "POST", body: expect.stringContaining("Reviewed") }));
    expect(fetchMock).toHaveBeenCalledWith("http://localhost:8000/api/v1/academic-years/year-1/hard-close/", expect.objectContaining({ method: "POST", body: expect.stringContaining("Final") }));
    const prepareCall = fetchMock.mock.calls.find(([url]) => url === "http://localhost:8000/api/v1/academic-year-rollovers/prepare/");
    expect(prepareCall).toBeDefined();
    const prepareHeaders = prepareCall?.[1]?.headers as Headers;
    expect(prepareHeaders.get("X-CSRFToken")).toBe("csrf-token-1");
  });
});
