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

export async function apiClientEnvelope<T>(path: string, init: RequestInit = {}): Promise<ApiEnvelope<T>> {
  const response = await fetch(buildUrl(path), {
    ...init,
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
      ...init.headers,
    },
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
