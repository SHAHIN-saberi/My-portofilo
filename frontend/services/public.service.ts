import { apiFetch } from "@/lib/api";
import {
  certificatesAdapter,
  coursesAdapter,
  educationAdapter,
  experiencesAdapter,
  profileAdapter,
  projectsAdapter,
  skillsAdapter,
  socialLinksAdapter,
} from "@/lib/adapters";
import {
  Certificate,
  Course,
  Education,
  Experience,
  Lang,
  Profile,
  Project,
  SafeAPIResponse,
  Skill,
  SocialLink,
} from "@/types";

export async function getProfileService(lang: Lang = "en"): Promise<SafeAPIResponse<Profile>> {
  const raw = await apiFetch(`/api/v1/profile?lang=${lang}`, {
    method: "GET",
    autoRetry: true,
  });
  return profileAdapter(raw);
}

export async function getSkillsService(
  lang: Lang = "en",
  category?: string
): Promise<SafeAPIResponse<Skill[]>> {
  let url = `/api/v1/skills?lang=${lang}`;
  if (category) {
    url += `&category=${encodeURIComponent(category)}`;
  }
  const raw = await apiFetch(url, {
    method: "GET",
    autoRetry: true,
  });
  return skillsAdapter(raw);
}

export async function getExperiencesService(lang: Lang = "en"): Promise<SafeAPIResponse<Experience[]>> {
  const raw = await apiFetch(`/api/v1/experiences?lang=${lang}`, {
    method: "GET",
    autoRetry: true,
  });
  return experiencesAdapter(raw);
}

export async function getProjectsService(
  lang: Lang = "en",
  featured?: boolean
): Promise<SafeAPIResponse<Project[]>> {
  let url = `/api/v1/projects?lang=${lang}`;
  if (featured !== undefined) {
    url += `&featured=${featured}`;
  }
  const raw = await apiFetch(url, {
    method: "GET",
    autoRetry: true,
  });
  return projectsAdapter(raw);
}

export async function getEducationService(lang: Lang = "en"): Promise<SafeAPIResponse<Education[]>> {
  const raw = await apiFetch(`/api/v1/education?lang=${lang}`, {
    method: "GET",
    autoRetry: true,
  });
  return educationAdapter(raw);
}

export async function getCoursesService(lang: Lang = "en"): Promise<SafeAPIResponse<Course[]>> {
  const raw = await apiFetch(`/api/v1/courses?lang=${lang}`, {
    method: "GET",
    autoRetry: true,
  });
  return coursesAdapter(raw);
}

export async function getCertificatesService(lang: Lang = "en"): Promise<SafeAPIResponse<Certificate[]>> {
  const raw = await apiFetch(`/api/v1/certificates?lang=${lang}`, {
    method: "GET",
    autoRetry: true,
  });
  return certificatesAdapter(raw);
}

export async function getSocialLinksService(): Promise<SafeAPIResponse<SocialLink[]>> {
  const raw = await apiFetch(`/api/v1/social-links`, {
    method: "GET",
    autoRetry: true,
  });
  return socialLinksAdapter(raw);
}
