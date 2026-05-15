import { afterEach, describe, expect, it, vi } from "vitest";
import {
  getClass,
  getClassEnrollment,
  getSubject,
  listClassEnrollments,
  listClasses,
  listClassSchedules,
  listEnrollmentBreaks,
  listEnrollmentDiscounts,
  listStudentWithdrawals,
  listSubjects,
  listTeacherTransfers,
} from "@/lib/classes";

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

describe("class API client", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("calls expected subject and class endpoints", async () => {
    const fetchMock = mockFetch([]);

    await listSubjects("math");
    await getSubject("subject-1");
    await listClasses();
    await getClass("class-1");

    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      "http://localhost:8000/api/v1/subjects/?search=math",
      expect.objectContaining({ credentials: "include" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      "http://localhost:8000/api/v1/subjects/subject-1/",
      expect.objectContaining({ credentials: "include" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      3,
      "http://localhost:8000/api/v1/classes/",
      expect.objectContaining({ credentials: "include" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      4,
      "http://localhost:8000/api/v1/classes/class-1/",
      expect.objectContaining({ credentials: "include" }),
    );
  });

  it("calls expected enrollment and related endpoints", async () => {
    const fetchMock = mockFetch([]);

    await listClassSchedules("grade");
    await listClassEnrollments();
    await getClassEnrollment("enrollment-1");
    await listEnrollmentBreaks();
    await listEnrollmentDiscounts();
    await listStudentWithdrawals();
    await listTeacherTransfers();

    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      "http://localhost:8000/api/v1/class-schedules/?search=grade",
      expect.objectContaining({ credentials: "include" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      "http://localhost:8000/api/v1/class-enrollments/",
      expect.objectContaining({ credentials: "include" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      3,
      "http://localhost:8000/api/v1/class-enrollments/enrollment-1/",
      expect.objectContaining({ credentials: "include" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      4,
      "http://localhost:8000/api/v1/class-enrollment-breaks/",
      expect.objectContaining({ credentials: "include" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      5,
      "http://localhost:8000/api/v1/class-enrollment-discounts/",
      expect.objectContaining({ credentials: "include" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      6,
      "http://localhost:8000/api/v1/student-withdrawals/",
      expect.objectContaining({ credentials: "include" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      7,
      "http://localhost:8000/api/v1/class-teacher-transfers/",
      expect.objectContaining({ credentials: "include" }),
    );
  });
});
