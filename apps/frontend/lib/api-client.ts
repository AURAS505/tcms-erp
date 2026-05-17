export interface ApiEnvelope<T> {
  success: boolean;
  data: T;
  message?: string;
  errors?: Record<string, string[]> | string[] | null;
  meta?: Record<string, unknown>;
}

export interface ApiPaginationMeta {
  count: number;
  page: number;
  page_size: number;
  next: string | null;
  previous: string | null;
}

const DEFAULT_API_BASE_URL = "http://localhost:8000";
const CSRF_ENDPOINT = "/api/v1/auth/csrf/";
const UNSAFE_METHODS = new Set(["POST", "PUT", "PATCH", "DELETE"]);
let cachedCsrfToken: string | null = null;

const getApiBaseUrl = () =>
  (process.env.NEXT_PUBLIC_API_BASE_URL ?? DEFAULT_API_BASE_URL).replace(/\/$/, "");

const buildUrl = (path: string) => {
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  const baseUrl = getApiBaseUrl();
  const apiPath =
    baseUrl.endsWith("/api") && normalizedPath.startsWith("/api/")
      ? normalizedPath.replace(/^\/api/, "")
      : normalizedPath;

  return `${baseUrl}${apiPath}`;
};

const getErrorMessage = <T>(payload: ApiEnvelope<T>) => {
  if (payload.message) return payload.message;
  if (Array.isArray(payload.errors)) return payload.errors.join(" ");
  if (payload.errors && typeof payload.errors === "object") {
    return Object.values(payload.errors).flat().join(" ");
  }
  return "Request failed";
};

const getCookieValue = (name: string) => {
  if (typeof document === "undefined") return null;
  const cookie = document.cookie
    .split(";")
    .map((part) => part.trim())
    .find((part) => part.startsWith(`${name}=`));
  return cookie ? decodeURIComponent(cookie.slice(name.length + 1)) : null;
};

const isUnsafeMethod = (method?: string) => UNSAFE_METHODS.has((method ?? "GET").toUpperCase());

export class ApiError extends Error {
  status: number;
  errors: ApiEnvelope<unknown>["errors"];

  constructor(message: string, status: number, errors?: ApiEnvelope<unknown>["errors"]) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.errors = errors;
  }
}

export function clearCsrfTokenCache() {
  cachedCsrfToken = null;
}

export async function fetchCsrfToken(): Promise<string> {
  if (cachedCsrfToken) return cachedCsrfToken;

  const response = await fetch(buildUrl(CSRF_ENDPOINT), {
    credentials: "include",
    headers: {
      Accept: "application/json",
    },
  });
  const payload = (await response.json().catch(() => null)) as ApiEnvelope<{ csrf_token?: string }> | null;

  if (!response.ok || !payload?.success) {
    throw new ApiError(
      payload ? getErrorMessage(payload) : "Unable to verify CSRF token",
      response.status,
      payload?.errors,
    );
  }

  const token = payload.data?.csrf_token || getCookieValue("csrftoken");
  if (!token) {
    throw new ApiError("Unable to verify CSRF token", response.status, payload.errors);
  }
  cachedCsrfToken = token;
  return token;
}

export async function apiClientEnvelope<T>(path: string, init: RequestInit = {}): Promise<ApiEnvelope<T>> {
  const headers = new Headers(init.headers);
  if (!headers.has("Content-Type")) headers.set("Content-Type", "application/json");
  if (!headers.has("Accept")) headers.set("Accept", "application/json");
  if (isUnsafeMethod(init.method) && !headers.has("X-CSRFToken")) {
    headers.set("X-CSRFToken", await fetchCsrfToken());
  }

  const response = await fetch(buildUrl(path), {
    ...init,
    credentials: "include",
    headers,
  });

  const payload = (await response.json().catch(() => null)) as ApiEnvelope<T> | null;

  if (!response.ok || !payload?.success) {
    throw new ApiError(
      payload ? getErrorMessage(payload) : response.statusText,
      response.status,
      payload?.errors,
    );
  }

  return payload;
}

export async function apiClient<T>(path: string, init: RequestInit = {}): Promise<T> {
  const payload = await apiClientEnvelope<T>(path, init);
  return payload.data;
}
