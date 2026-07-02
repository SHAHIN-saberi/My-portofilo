/**
 * Server-side API fetch helper for Server Components
 * Fetches data directly from the backend API without going through the client-side apiFetch
 */

import { Lang } from "@/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface FetchOptions {
  revalidate?: number; // ISR revalidation in seconds
}

async function serverFetch<T>(
  endpoint: string,
  options: FetchOptions = {}
): Promise<T | null> {
  try {
    const url = `${API_URL}${endpoint.startsWith("/") ? endpoint : `/${endpoint}`}`;
    const response = await fetch(url, {
      next: { revalidate: options.revalidate ?? 60 },
    });

    if (!response.ok) {
      console.error(`Server fetch failed: ${response.status} ${response.statusText}`);
      return null;
    }

    return await response.json();
  } catch (error) {
    console.error("Server fetch error:", error);
    return null;
  }
}

// Public API fetchers for Server Components
export async function getProfileServer(lang: Lang = "en", revalidate = 60) {
  const data = await serverFetch<{ data: any }>(
    `/api/v1/profile?lang=${lang}`,
    { revalidate }
  );
  return data?.data || null;
}

export async function getSkillsServer(lang: Lang = "en", revalidate = 60) {
  const data = await serverFetch<{ data: any[] }>(
    `/api/v1/skills?lang=${lang}`,
    { revalidate }
  );
  return data?.data || [];
}

export async function getProjectsServer(lang: Lang = "en", featured?: boolean, revalidate = 60) {
  let url = `/api/v1/projects?lang=${lang}`;
  if (featured !== undefined) {
    url += `&featured=${featured}`;
  }
  const data = await serverFetch<{ data: any[] }>(url, { revalidate });
  return data?.data || [];
}

export async function getExperiencesServer(lang: Lang = "en", revalidate = 60) {
  const data = await serverFetch<{ data: any[] }>(
    `/api/v1/experiences?lang=${lang}`,
    { revalidate }
  );
  return data?.data || [];
}

export async function getEducationServer(lang: Lang = "en", revalidate = 60) {
  const data = await serverFetch<{ data: any[] }>(
    `/api/v1/education?lang=${lang}`,
    { revalidate }
  );
  return data?.data || [];
}

export async function getCoursesServer(lang: Lang = "en", revalidate = 60) {
  const data = await serverFetch<{ data: any[] }>(
    `/api/v1/courses?lang=${lang}`,
    { revalidate }
  );
  return data?.data || [];
}

export async function getCertificatesServer(lang: Lang = "en", revalidate = 60) {
  const data = await serverFetch<{ data: any[] }>(
    `/api/v1/certificates?lang=${lang}`,
    { revalidate }
  );
  return data?.data || [];
}

export async function getSocialLinksServer(revalidate = 60) {
  const data = await serverFetch<{ data: any[] }>(
    `/api/v1/social-links`,
    { revalidate }
  );
  return data?.data || [];
}
