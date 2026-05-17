import { afterEach, describe, expect, it, vi } from "vitest";
import { apiClient, clearCsrfTokenCache } from "@/lib/api-client";

const envelope = (data: unknown) => ({
  success: true,
  data,
  errors: null,
  meta: {},
});

describe("apiClient CSRF handling", () => {
  afterEach(() => {
    clearCsrfTokenCache();
    vi.unstubAllGlobals();
  });

  it("does not fetch CSRF token before GET requests", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: vi.fn().mockResolvedValue(envelope({ id: "resource-1" })),
    });
    vi.stubGlobal("fetch", fetchMock);

    await apiClient("/api/v1/resources/");

    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(fetchMock).toHaveBeenCalledWith("http://localhost:8000/api/v1/resources/", expect.objectContaining({ credentials: "include" }));
  });

  it("fetches and sends CSRF token before POST requests", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: vi.fn().mockResolvedValue(envelope({ csrf_token: "csrf-token-1" })),
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: vi.fn().mockResolvedValue(envelope({ id: "created-1" })),
      });
    vi.stubGlobal("fetch", fetchMock);

    await apiClient("/api/v1/resources/", { method: "POST", body: "{}" });

    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      "http://localhost:8000/api/v1/auth/csrf/",
      expect.objectContaining({ credentials: "include" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      "http://localhost:8000/api/v1/resources/",
      expect.objectContaining({
        method: "POST",
        credentials: "include",
        headers: expect.any(Headers),
      }),
    );
    expect((fetchMock.mock.calls[1][1].headers as Headers).get("X-CSRFToken")).toBe("csrf-token-1");
  });

  it("reuses cached CSRF token for later mutation requests", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: vi.fn().mockResolvedValue(envelope({ csrf_token: "csrf-token-1" })),
      })
      .mockResolvedValue({
        ok: true,
        status: 200,
        json: vi.fn().mockResolvedValue(envelope({ id: "updated" })),
      });
    vi.stubGlobal("fetch", fetchMock);

    await apiClient("/api/v1/resources/1/", { method: "PATCH", body: "{}" });
    await apiClient("/api/v1/resources/2/", { method: "DELETE" });

    expect(fetchMock).toHaveBeenCalledTimes(3);
    expect(fetchMock.mock.calls[0][0]).toBe("http://localhost:8000/api/v1/auth/csrf/");
    expect((fetchMock.mock.calls[1][1].headers as Headers).get("X-CSRFToken")).toBe("csrf-token-1");
    expect((fetchMock.mock.calls[2][1].headers as Headers).get("X-CSRFToken")).toBe("csrf-token-1");
  });

  it("surfaces clear error when CSRF token cannot be fetched", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: false,
      status: 403,
      json: vi.fn().mockResolvedValue({ success: false, data: null, message: "CSRF unavailable", errors: null }),
    });
    vi.stubGlobal("fetch", fetchMock);

    await expect(apiClient("/api/v1/resources/", { method: "POST", body: "{}" })).rejects.toThrow("CSRF unavailable");
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });
});
