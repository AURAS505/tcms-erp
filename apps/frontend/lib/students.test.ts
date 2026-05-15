import { afterEach, describe, expect, it, vi } from "vitest";
import { getStudent, getStudentInquiry, listStudentInquiries, listStudents } from "@/lib/students";

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

describe("student API client", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("calls expected student inquiry endpoints", async () => {
    const fetchMock = mockFetch([]);

    await listStudentInquiries("ram");
    await getStudentInquiry("inquiry-1");

    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      "http://localhost:8000/api/v1/student-inquiries/?search=ram",
      expect.objectContaining({ credentials: "include" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      "http://localhost:8000/api/v1/student-inquiries/inquiry-1/",
      expect.objectContaining({ credentials: "include" }),
    );
  });

  it("calls expected student endpoints", async () => {
    const fetchMock = mockFetch([]);

    await listStudents();
    await getStudent("student-1");

    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      "http://localhost:8000/api/v1/students/",
      expect.objectContaining({ credentials: "include" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      "http://localhost:8000/api/v1/students/student-1/",
      expect.objectContaining({ credentials: "include" }),
    );
  });
});

