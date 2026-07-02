import {
  AdminEducation,
  AdminExperience,
  AdminProfile,
  AdminProject,
  AdminSkill,
  MessageResponse,
  SafeAPIResponse,
  TokenResponse,
} from "@/types";
import {
  adaptEducationItem,
  adaptExperienceItem,
  adaptProfileItem,
  adaptProjectItem,
  adaptSkillItem,
} from "./public.adapter";
import { baseEnvelopeAdapter, safeArray, safeNumber, safeString } from "./base.adapter";

export function adminLoginAdapter(raw: unknown): SafeAPIResponse<TokenResponse> {
  if (!raw || typeof raw !== "object") {
    return {
      data: { access_token: "", expires_in_minutes: 0 },
      meta: {},
      isValid: false,
    };
  }
  const item = raw as Record<string, any>;
  const token = safeString(item.access_token, "");
  return {
    data: {
      access_token: token || "",
      expires_in_minutes: safeNumber(item.expires_in_minutes, 60) || 60,
    },
    meta: {},
    isValid: Boolean(token),
  };
}

export function adminWhoAmIAdapter(raw: unknown): SafeAPIResponse<{ email: string; role: string }> {
  return baseEnvelopeAdapter<{ email: string; role: string }>(
    raw,
    (itemRaw) => {
      const item = (itemRaw && typeof itemRaw === "object" ? itemRaw : {}) as Record<string, any>;
      return {
        email: safeString(item.email, "") || "",
        role: safeString(item.role, "admin") || "admin",
      };
    },
    { email: "", role: "admin" }
  );
}

export function adaptAdminProfileItem(raw: unknown): AdminProfile {
  if (!raw || typeof raw !== "object") return {};
  const base = adaptProfileItem(raw);
  const item = raw as Record<string, any>;

  const transRawList = Array.isArray(item.translations) ? item.translations : [];
  const translations = transRawList.map((t: any) => ({
    lang: (safeString(t?.lang, "en") as "en" | "fa") || "en",
    title: safeString(t?.title, null),
    summary: safeString(t?.summary, null),
    bio: safeString(t?.bio, null),
  }));

  const { translation, ...rest } = base;
  return {
    ...rest,
    translations,
  };
}

export function adminProfileAdapter(raw: unknown): SafeAPIResponse<AdminProfile> {
  return baseEnvelopeAdapter<AdminProfile>(raw, adaptAdminProfileItem, {});
}

export function adaptAdminSkillItem(raw: unknown): AdminSkill {
  if (!raw || typeof raw !== "object") return { id: 0 };
  const base = adaptSkillItem(raw);
  const item = raw as Record<string, any>;

  const transRawList = Array.isArray(item.translations) ? item.translations : [];
  const translations = transRawList.map((t: any) => ({
    lang: (safeString(t?.lang, "en") as "en" | "fa") || "en",
    name: safeString(t?.name, null),
    description: safeString(t?.description, null),
  }));

  const { translation, ...rest } = base;
  return {
    ...rest,
    translations,
  };
}

export function adminSkillsAdapter(raw: unknown): SafeAPIResponse<AdminSkill[]> {
  return baseEnvelopeAdapter<AdminSkill[]>(raw, (data) => safeArray(data, adaptAdminSkillItem), []);
}

export function adaptAdminExperienceItem(raw: unknown): AdminExperience {
  if (!raw || typeof raw !== "object") return { id: 0 };
  const base = adaptExperienceItem(raw);
  const item = raw as Record<string, any>;

  const transRawList = Array.isArray(item.translations) ? item.translations : [];
  const translations = transRawList.map((t: any) => ({
    lang: (safeString(t?.lang, "en") as "en" | "fa") || "en",
    role: safeString(t?.role, null),
    description: safeString(t?.description, null),
  }));

  const { translation, ...rest } = base;
  return {
    ...rest,
    translations,
  };
}

export function adminExperiencesAdapter(raw: unknown): SafeAPIResponse<AdminExperience[]> {
  return baseEnvelopeAdapter<AdminExperience[]>(raw, (data) => safeArray(data, adaptAdminExperienceItem), []);
}

export function adaptAdminProjectItem(raw: unknown): AdminProject {
  if (!raw || typeof raw !== "object") return { id: 0 };
  const base = adaptProjectItem(raw);
  const item = raw as Record<string, any>;

  const transRawList = Array.isArray(item.translations) ? item.translations : [];
  const translations = transRawList.map((t: any) => ({
    lang: (safeString(t?.lang, "en") as "en" | "fa") || "en",
    title: safeString(t?.title, null),
    short_description: safeString(t?.short_description, null),
    description: safeString(t?.description, null),
    role: safeString(t?.role, null),
    impact: safeString(t?.impact, null),
  }));

  const { translation, ...rest } = base;
  return {
    ...rest,
    translations,
  };
}

export function adminProjectsAdapter(raw: unknown): SafeAPIResponse<AdminProject[]> {
  return baseEnvelopeAdapter<AdminProject[]>(raw, (data) => safeArray(data, adaptAdminProjectItem), []);
}

export function adaptAdminEducationItem(raw: unknown): AdminEducation {
  if (!raw || typeof raw !== "object") return { id: 0 };
  const base = adaptEducationItem(raw);
  const item = raw as Record<string, any>;

  const transRawList = Array.isArray(item.translations) ? item.translations : [];
  const translations = transRawList.map((t: any) => ({
    lang: (safeString(t?.lang, "en") as "en" | "fa") || "en",
    degree: safeString(t?.degree, null),
    field_of_study: safeString(t?.field_of_study, null),
    description: safeString(t?.description, null),
  }));

  const { translation, ...rest } = base;
  return {
    ...rest,
    translations,
  };
}

export function adminEducationAdapter(raw: unknown): SafeAPIResponse<AdminEducation[]> {
  return baseEnvelopeAdapter<AdminEducation[]>(raw, (data) => safeArray(data, adaptAdminEducationItem), []);
}

export function adminIdResultAdapter(raw: unknown): SafeAPIResponse<{ id: number }> {
  return baseEnvelopeAdapter<{ id: number }>(
    raw,
    (itemRaw) => {
      const item = (itemRaw && typeof itemRaw === "object" ? itemRaw : {}) as Record<string, any>;
      return {
        id: safeNumber(item.id, 0) || 0,
      };
    },
    { id: 0 }
  );
}

export function adminMessageResultAdapter(raw: unknown): SafeAPIResponse<MessageResponse> {
  if (!raw || typeof raw !== "object") {
    return {
      data: { message: "Operation completed." },
      meta: {},
      isValid: false,
    };
  }
  const item = raw as Record<string, any>;
  const msg = safeString(item.message, "") || "Operation completed.";
  return {
    data: { message: msg },
    meta: {},
    isValid: true,
  };
}

export function adminKnowledgeStatusAdapter(raw: unknown): SafeAPIResponse<{
  chunk_count: number;
  last_indexed_at: string | null;
}> {
  return baseEnvelopeAdapter<{ chunk_count: number; last_indexed_at: string | null }>(
    raw,
    (itemRaw) => {
      const item = (itemRaw && typeof itemRaw === "object" ? itemRaw : {}) as Record<string, any>;
      return {
        chunk_count: safeNumber(item.chunk_count, 0) || 0,
        last_indexed_at: safeString(item.last_indexed_at, null),
      };
    },
    { chunk_count: 0, last_indexed_at: null }
  );
}
