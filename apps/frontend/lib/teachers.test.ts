import { afterEach, describe, expect, it, vi } from "vitest";
import {
  getTeacher,
  getTeacherContract,
  listTeacherActivities,
  listTeacherContracts,
  listTeachers,
  listTeacherStatusHistory,
} from "@/lib/teachers";

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

describe("teacher API client", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("calls expected teacher endpoints", async () => {
    const fetchMock = mockFetch([]);

    await listTeachers("rita");
    await getTeacher("teacher-1");

    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      "http://localhost:8000/api/v1/teachers/?search=rita",
      expect.objectContaining({ credentials: "include" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      "http://localhost:8000/api/v1/teachers/teacher-1/",
      expect.objectContaining({ credentials: "include" }),
    );
  });

  it("calls expected teacher contract and history endpoints", async () => {
    const fetchMock = mockFetch([]);

    await listTeacherContracts();
    await getTeacherContract("contract-1");
    await listTeacherActivities("follow");
    await listTeacherStatusHistory();

    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      "http://localhost:8000/api/v1/teacher-contracts/",
      expect.objectContaining({ credentials: "include" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      "http://localhost:8000/api/v1/teacher-contracts/contract-1/",
      expect.objectContaining({ credentials: "include" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      3,
      "http://localhost:8000/api/v1/teacher-activities/?search=follow",
      expect.objectContaining({ credentials: "include" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      4,
      "http://localhost:8000/api/v1/teacher-status-history/",
      expect.objectContaining({ credentials: "include" }),
    );
  });
});
