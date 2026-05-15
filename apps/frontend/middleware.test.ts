import { describe, expect, it } from "vitest";
import { NextRequest } from "next/server";
import { middleware } from "@/middleware";

const makeRequest = (path: string, cookie?: string) =>
  new NextRequest(`http://localhost:3000${path}`, {
    headers: cookie ? { cookie } : undefined,
  });

describe("middleware", () => {
  it("redirects unauthenticated dashboard requests to login", () => {
    const response = middleware(makeRequest("/dashboard/reports?tab=summary"));

    expect(response.status).toBe(307);
    expect(response.headers.get("location")).toBe(
      "http://localhost:3000/login?redirect=%2Fdashboard%2Freports%3Ftab%3Dsummary",
    );
  });

  it("allows dashboard requests with a Django session cookie", () => {
    const response = middleware(makeRequest("/dashboard", "sessionid=abc123"));

    expect(response.status).toBe(200);
    expect(response.headers.get("location")).toBeNull();
  });

  it("allows public auth routes", () => {
    const response = middleware(makeRequest("/login"));

    expect(response.status).toBe(200);
    expect(response.headers.get("location")).toBeNull();
  });
});

