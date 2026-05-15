import { afterEach, describe, expect, it, vi } from "vitest";
import { getFamily, getGuardian, listFamilies, listGuardians, listStudentGuardians } from "@/lib/guardians";

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

describe("guardian API client", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("calls expected family endpoints", async () => {
    const fetchMock = mockFetch([]);

    await listFamilies("FAM");
    await getFamily("family-1");

    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      "http://localhost:8000/api/v1/families/?search=FAM",
      expect.objectContaining({ credentials: "include" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      "http://localhost:8000/api/v1/families/family-1/",
      expect.objectContaining({ credentials: "include" }),
    );
  });

  it("calls expected guardian endpoints", async () => {
    const fetchMock = mockFetch([]);

    await listGuardians();
    await getGuardian("guardian-1");
    await listStudentGuardians("ADM-001");

    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      "http://localhost:8000/api/v1/guardians/",
      expect.objectContaining({ credentials: "include" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      "http://localhost:8000/api/v1/guardians/guardian-1/",
      expect.objectContaining({ credentials: "include" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      3,
      "http://localhost:8000/api/v1/student-guardians/?search=ADM-001",
      expect.objectContaining({ credentials: "include" }),
    );
  });
});

