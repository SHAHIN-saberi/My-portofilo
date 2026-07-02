import { SafeError } from "@/types";

export function errorAdapter(rawError: unknown): SafeError {
  if (!rawError && rawError !== 0 && rawError !== false) {
    return {
      message: "An undefined error occurred.",
      status: 500,
      code: "UNDEFINED_ERROR",
      isNormalized: true,
      rawError,
    };
  }

  if (typeof rawError === "object" && rawError !== null && "isNormalized" in rawError && (rawError as SafeError).isNormalized === true) {
    return rawError as SafeError;
  }

  // Handle known HTTP status structures or custom ApiError objects
  if (typeof rawError === "object" && rawError !== null) {
    const errObj = rawError as Record<string, any>;
    const status = typeof errObj.status === "number" ? errObj.status : 500;
    const msg = typeof errObj.message === "string" && errObj.message ? errObj.message : "An error occurred.";

    if (status === 401 || errObj.code === "UNAUTHORIZED") {
      return {
        message: "Unauthorized: Please log in again.",
        status: 401,
        code: "UNAUTHORIZED",
        isNormalized: true,
        rawError,
      };
    }

    if (status === 429 || errObj.code === "RATE_LIMIT") {
      return {
        message: "Please wait a moment before asking again.",
        status: 429,
        code: "RATE_LIMIT",
        isNormalized: true,
        rawError,
      };
    }

    if (errObj.name === "AbortError" || errObj.code === "TIMEOUT" || status === 408) {
      return {
        message: "Request timed out. Please try again.",
        status: 408,
        code: "TIMEOUT",
        isNormalized: true,
        rawError,
      };
    }

    if (msg.includes("JSON") || msg.includes("parse") || status === 502) {
      return {
        message: "Malformed data received from backend.",
        status: 502,
        code: "MALFORMED_JSON",
        isNormalized: true,
        rawError,
      };
    }

    return {
      message: msg,
      status,
      code: errObj.code || `HTTP_${status}`,
      isNormalized: true,
      rawError,
    };
  }

  if (typeof rawError === "string") {
    return {
      message: rawError,
      status: 500,
      code: "STRING_ERROR",
      isNormalized: true,
      rawError,
    };
  }

  return {
    message: "Unexpected network error.",
    status: 500,
    code: "UNKNOWN_ERROR",
    isNormalized: true,
    rawError,
  };
}
