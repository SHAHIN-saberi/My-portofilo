import { SafeError } from "@/types";
import { errorAdapter } from "./adapters/error.adapter";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface ApiFetchOptions extends RequestInit {
  autoRetry?: boolean;
  timeoutMs?: number;
}

export class ApiError extends Error {
  status?: number;
  code?: string;

  constructor(message: string, status?: number, code?: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
  }
}

export function normalizeError(error: unknown): SafeError {
  return errorAdapter(error);
}

export async function apiFetch<T = unknown>(endpoint: string, options: ApiFetchOptions = {}): Promise<unknown> {
  const { autoRetry = false, timeoutMs = 30000, headers = {}, ...restOptions } = options;
  const url = `${API_URL}${endpoint.startsWith("/") ? endpoint : `/${endpoint}`}`;

  const mergedHeaders: Record<string, string> = {
    "Content-Type": "application/json",
    ...(headers as Record<string, string>),
  };

  const attemptFetch = async (): Promise<Response> => {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

    try {
      const response = await fetch(url, {
        ...restOptions,
        headers: mergedHeaders,
        signal: controller.signal,
        credentials: "include", // Send HttpOnly cookies with request
      });
      return response;
    } finally {
      clearTimeout(timeoutId);
    }
  };

  try {
    let response = await attemptFetch();

    if (!response.ok && autoRetry && response.status !== 401 && response.status !== 429) {
      response = await attemptFetch();
    }

    if (!response.ok) {
      let errDetail = `${response.status} ${response.statusText}`;
      try {
        const errJson = await response.json();
        if (errJson && errJson.error && errJson.error.message) {
          errDetail = errJson.error.message;
        } else if (errJson && errJson.detail) {
          errDetail = typeof errJson.detail === "string" ? errJson.detail : JSON.stringify(errJson.detail);
        }
      } catch {
        // Fallback to HTTP status text
      }
      throw new ApiError(errDetail, response.status);
    }

    const text = await response.text();
    if (!text) {
      return {};
    }
    try {
      const data = JSON.parse(text);
      if (data === null || typeof data !== "object") {
        throw new ApiError("Invalid response format received from server", 502);
      }
      return data;
    } catch (parseErr) {
      if (parseErr instanceof ApiError) throw parseErr;
      throw new ApiError("Failed to parse JSON response", 502);
    }
  } catch (error) {
    if (autoRetry && !(error instanceof ApiError) && error instanceof Error && error.name !== "AbortError") {
      try {
        const response = await attemptFetch();
        if (!response.ok) {
          throw new ApiError(`${response.status} ${response.statusText}`, response.status);
        }
        const data = await response.json();
        return data;
      } catch {
        throw error;
      }
    }
    throw error;
  }
}
