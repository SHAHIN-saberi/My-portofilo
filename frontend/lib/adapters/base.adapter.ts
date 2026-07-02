import { SafeAPIResponse } from "@/types";

export function safeString(val: unknown, fallback: string | null = null): string | null {
  if (val === undefined || val === null) return fallback;
  if (typeof val === "string") return val;
  return String(val);
}

export function safeNumber(val: unknown, fallback: number | null = null): number | null {
  if (val === undefined || val === null) return fallback;
  if (typeof val === "number" && !isNaN(val)) return val;
  const parsed = Number(val);
  return isNaN(parsed) ? fallback : parsed;
}

export function safeBoolean(val: unknown, fallback: boolean | null = null): boolean | null {
  if (val === undefined || val === null) return fallback;
  if (typeof val === "boolean") return val;
  if (val === "true" || val === 1) return true;
  if (val === "false" || val === 0) return false;
  return fallback;
}

export function safeArray<T>(val: unknown, itemAdapter: (item: unknown) => T): T[] {
  if (!Array.isArray(val)) return [];
  return val.map((item) => itemAdapter(item));
}

export function baseEnvelopeAdapter<T>(
  raw: unknown,
  dataAdapter: (rawData: unknown) => T,
  fallbackData: T
): SafeAPIResponse<T> {
  if (raw === undefined || raw === null || typeof raw !== "object") {
    return {
      data: fallbackData,
      meta: {},
      isValid: false,
    };
  }

  const rawObj = raw as Record<string, any>;
  const rawData = "data" in rawObj ? rawObj.data : rawObj;
  const meta = rawObj.meta && typeof rawObj.meta === "object" ? rawObj.meta : {};

  try {
    const data = rawData !== undefined && rawData !== null ? dataAdapter(rawData) : fallbackData;
    return {
      data,
      meta,
      isValid: true,
    };
  } catch {
    return {
      data: fallbackData,
      meta,
      isValid: false,
    };
  }
}
