import { afterEach, describe, expect, it, vi } from "vitest";
import { listAcademicPeriods, listAcademicYears, listBranches, listOrganizations } from "@/lib/lookups";

const mockFetch = () => {
  const fetchMock = vi.fn().mockResolvedValue({
    ok: true,
    status: 200,
    json: vi.fn().mockResolvedValue({
      success: true,
      data: [],
      errors: null,
      meta: { pagination: { count: 0, page: 1, page_size: 25, next: null, previous: null } },
    }),
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
};

describe("lookup API client", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("calls expected lookup endpoints", async () => {
    const fetchMock = mockFetch();

    await listOrganizations();
    await listBranches();
    await listAcademicYears();
    await listAcademicPeriods();

    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      "http://localhost:8000/api/v1/organizations/",
      expect.objectContaining({ credentials: "include" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      "http://localhost:8000/api/v1/branches/",
      expect.objectContaining({ credentials: "include" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      3,
      "http://localhost:8000/api/v1/academic-years/",
      expect.objectContaining({ credentials: "include" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      4,
      "http://localhost:8000/api/v1/academic-periods/",
      expect.objectContaining({ credentials: "include" }),
    );
  });
});
