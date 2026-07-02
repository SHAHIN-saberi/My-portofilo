import {
  baseEnvelopeAdapter,
  safeArray,
  safeBoolean,
  safeNumber,
  safeString,
} from "./base.adapter";
import {
  Certificate,
  Course,
  Education,
  Experience,
  Profile,
  Project,
  SafeAPIResponse,
  Skill,
  SocialLink,
} from "@/types";

export function adaptProfileItem(raw: unknown): Profile {
  if (!raw || typeof raw !== "object") return {};
  const item = raw as Record<string, any>;
  const transRaw = item.translation && typeof item.translation === "object" ? item.translation : {};

  return {
    id: safeNumber(item.id, undefined) || undefined,
    name: safeString(item.name, null),
    photo_url: safeString(item.photo_url, null),
    email: safeString(item.email, null),
    phone: safeString(item.phone, null),
    location: safeString(item.location, null),
    availability_status: safeString(item.availability_status, null),
    github_url: safeString(item.github_url, null),
    linkedin_url: safeString(item.linkedin_url, null),
    website_url: safeString(item.website_url, null),
    cv_pdf_url: safeString(item.cv_pdf_url, null),
    translation: {
      lang: (safeString(transRaw.lang, "en") as "en" | "fa") || "en",
      title: safeString(transRaw.title, null),
      summary: safeString(transRaw.summary, null),
      bio: safeString(transRaw.bio, null),
    },
  };
}

export function profileAdapter(raw: unknown): SafeAPIResponse<Profile> {
  return baseEnvelopeAdapter<Profile>(raw, adaptProfileItem, {});
}

export function adaptSkillItem(raw: unknown): Skill {
  if (!raw || typeof raw !== "object") {
    return { id: 0 };
  }
  const item = raw as Record<string, any>;
  const transRaw = item.translation && typeof item.translation === "object" ? item.translation : {};

  return {
    id: safeNumber(item.id, 0) || 0,
    category: safeString(item.category, null),
    proficiency: safeString(item.proficiency, null),
    years_experience: safeNumber(item.years_experience, null),
    display_order: safeNumber(item.display_order, null),
    translation: {
      lang: (safeString(transRaw.lang, "en") as "en" | "fa") || "en",
      name: safeString(transRaw.name, null),
      description: safeString(transRaw.description, null),
    },
  };
}

export function skillsAdapter(raw: unknown): SafeAPIResponse<Skill[]> {
  return baseEnvelopeAdapter<Skill[]>(raw, (data) => safeArray(data, adaptSkillItem), []);
}

export function adaptExperienceItem(raw: unknown): Experience {
  if (!raw || typeof raw !== "object") {
    return { id: 0 };
  }
  const item = raw as Record<string, any>;
  const transRaw = item.translation && typeof item.translation === "object" ? item.translation : {};

  return {
    id: safeNumber(item.id, 0) || 0,
    company: safeString(item.company, null),
    start_date: safeString(item.start_date, null),
    end_date: safeString(item.end_date, null),
    is_current: safeBoolean(item.is_current, null),
    location: safeString(item.location, null),
    display_order: safeNumber(item.display_order, null),
    translation: {
      lang: (safeString(transRaw.lang, "en") as "en" | "fa") || "en",
      role: safeString(transRaw.role, null),
      description: safeString(transRaw.description, null),
    },
  };
}

export function experiencesAdapter(raw: unknown): SafeAPIResponse<Experience[]> {
  return baseEnvelopeAdapter<Experience[]>(raw, (data) => safeArray(data, adaptExperienceItem), []);
}

export function adaptProjectItem(raw: unknown): Project {
  if (!raw || typeof raw !== "object") {
    return { id: 0 };
  }
  const item = raw as Record<string, any>;
  const transRaw = item.translation && typeof item.translation === "object" ? item.translation : {};

  return {
    id: safeNumber(item.id, 0) || 0,
    start_date: safeString(item.start_date, null),
    end_date: safeString(item.end_date, null),
    live_url: safeString(item.live_url, null),
    github_url: safeString(item.github_url, null),
    tech_stack: Array.isArray(item.tech_stack) ? item.tech_stack.map((t: any) => String(t)) : [],
    featured: safeBoolean(item.featured, null),
    display_order: safeNumber(item.display_order, null),
    skill_ids: Array.isArray(item.skill_ids) ? item.skill_ids.map((id: any) => Number(id)).filter((n: number) => !isNaN(n)) : [],
    translation: {
      lang: (safeString(transRaw.lang, "en") as "en" | "fa") || "en",
      title: safeString(transRaw.title, null),
      short_description: safeString(transRaw.short_description, null),
      description: safeString(transRaw.description, null),
      role: safeString(transRaw.role, null),
      impact: safeString(transRaw.impact, null),
    },
  };
}

export function projectsAdapter(raw: unknown): SafeAPIResponse<Project[]> {
  return baseEnvelopeAdapter<Project[]>(raw, (data) => safeArray(data, adaptProjectItem), []);
}

export function adaptEducationItem(raw: unknown): Education {
  if (!raw || typeof raw !== "object") {
    return { id: 0 };
  }
  const item = raw as Record<string, any>;
  const transRaw = item.translation && typeof item.translation === "object" ? item.translation : {};

  return {
    id: safeNumber(item.id, 0) || 0,
    institution: safeString(item.institution, null),
    start_date: safeString(item.start_date, null),
    end_date: safeString(item.end_date, null),
    location: safeString(item.location, null),
    display_order: safeNumber(item.display_order, null),
    translation: {
      lang: (safeString(transRaw.lang, "en") as "en" | "fa") || "en",
      degree: safeString(transRaw.degree, null),
      field_of_study: safeString(transRaw.field_of_study, null),
      description: safeString(transRaw.description, null),
    },
  };
}

export function educationAdapter(raw: unknown): SafeAPIResponse<Education[]> {
  return baseEnvelopeAdapter<Education[]>(raw, (data) => safeArray(data, adaptEducationItem), []);
}

export function adaptCourseItem(raw: unknown): Course {
  if (!raw || typeof raw !== "object") {
    return { id: 0 };
  }
  const item = raw as Record<string, any>;
  const transRaw = item.translation && typeof item.translation === "object" ? item.translation : {};

  return {
    id: safeNumber(item.id, 0) || 0,
    provider: safeString(item.provider, null),
    completion_date: safeString(item.completion_date, null),
    credential_url: safeString(item.credential_url, null),
    display_order: safeNumber(item.display_order, null),
    translation: {
      lang: (safeString(transRaw.lang, "en") as "en" | "fa") || "en",
      title: safeString(transRaw.title, null),
      description: safeString(transRaw.description, null),
    },
  };
}

export function coursesAdapter(raw: unknown): SafeAPIResponse<Course[]> {
  return baseEnvelopeAdapter<Course[]>(raw, (data) => safeArray(data, adaptCourseItem), []);
}

export function adaptCertificateItem(raw: unknown): Certificate {
  if (!raw || typeof raw !== "object") {
    return { id: 0 };
  }
  const item = raw as Record<string, any>;
  const transRaw = item.translation && typeof item.translation === "object" ? item.translation : {};

  return {
    id: safeNumber(item.id, 0) || 0,
    issuer: safeString(item.issuer, null),
    issue_date: safeString(item.issue_date, null),
    credential_url: safeString(item.credential_url, null),
    display_order: safeNumber(item.display_order, null),
    translation: {
      lang: (safeString(transRaw.lang, "en") as "en" | "fa") || "en",
      title: safeString(transRaw.title, null),
      description: safeString(transRaw.description, null),
    },
  };
}

export function certificatesAdapter(raw: unknown): SafeAPIResponse<Certificate[]> {
  return baseEnvelopeAdapter<Certificate[]>(raw, (data) => safeArray(data, adaptCertificateItem), []);
}

export function adaptSocialLinkItem(raw: unknown): SocialLink {
  if (!raw || typeof raw !== "object") {
    return { id: 0 };
  }
  const item = raw as Record<string, any>;

  return {
    id: safeNumber(item.id, 0) || 0,
    platform: safeString(item.platform, null),
    url: safeString(item.url, null),
    display_order: safeNumber(item.display_order, null),
    is_visible: safeBoolean(item.is_visible, true),
  };
}

export function socialLinksAdapter(raw: unknown): SafeAPIResponse<SocialLink[]> {
  return baseEnvelopeAdapter<SocialLink[]>(raw, (data) => safeArray(data, adaptSocialLinkItem), []);
}
