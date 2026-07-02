import { apiFetch } from "@/lib/api";
import {
  adminEducationAdapter,
  adminExperiencesAdapter,
  adminIdResultAdapter,
  adminKnowledgeStatusAdapter,
  adminLoginAdapter,
  adminMessageResultAdapter,
  adminProfileAdapter,
  adminProjectsAdapter,
  adminSkillsAdapter,
  adminWhoAmIAdapter,
} from "@/lib/adapters";
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

export async function adminLoginService(email: string, password: string): Promise<SafeAPIResponse<TokenResponse>> {
  const raw = await apiFetch("/api/v1/admin/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
  return adminLoginAdapter(raw);
}

export async function getWhoAmIService(): Promise<SafeAPIResponse<{ email: string; role: string }>> {
  const raw = await apiFetch("/api/v1/admin/me", {
    method: "GET",
  });
  return adminWhoAmIAdapter(raw);
}

export async function getAdminProfileService(lang: string = "en"): Promise<SafeAPIResponse<AdminProfile>> {
  const raw = await apiFetch(`/api/v1/admin/profile?lang=${lang}`, {
    method: "GET",
  });
  return adminProfileAdapter(raw);
}

export async function updateAdminProfileService(payload: AdminProfile): Promise<SafeAPIResponse<AdminProfile>> {
  const raw = await apiFetch("/api/v1/admin/profile", {
    method: "PUT",
    body: JSON.stringify(payload),
  });
  return adminProfileAdapter(raw);
}

export async function listAdminSkillsService(): Promise<SafeAPIResponse<AdminSkill[]>> {
  const raw = await apiFetch("/api/v1/admin/skills", {
    method: "GET",
  });
  return adminSkillsAdapter(raw);
}

export async function createAdminSkillService(payload: AdminSkill): Promise<SafeAPIResponse<{ id: number }>> {
  const raw = await apiFetch("/api/v1/admin/skills", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  return adminIdResultAdapter(raw);
}

export async function updateAdminSkillService(
  id: number,
  payload: AdminSkill
): Promise<SafeAPIResponse<{ id: number }>> {
  const raw = await apiFetch(`/api/v1/admin/skills/${id}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
  return adminIdResultAdapter(raw);
}

export async function deleteAdminSkillService(id: number): Promise<SafeAPIResponse<MessageResponse>> {
  const raw = await apiFetch(`/api/v1/admin/skills/${id}`, {
    method: "DELETE",
  });
  return adminMessageResultAdapter(raw);
}

export async function listAdminExperiencesService(): Promise<SafeAPIResponse<AdminExperience[]>> {
  const raw = await apiFetch("/api/v1/admin/experiences", {
    method: "GET",
  });
  return adminExperiencesAdapter(raw);
}

export async function createAdminExperienceService(
  payload: AdminExperience
): Promise<SafeAPIResponse<{ id: number }>> {
  const raw = await apiFetch("/api/v1/admin/experiences", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  return adminIdResultAdapter(raw);
}

export async function updateAdminExperienceService(
  id: number,
  payload: AdminExperience
): Promise<SafeAPIResponse<{ id: number }>> {
  const raw = await apiFetch(`/api/v1/admin/experiences/${id}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
  return adminIdResultAdapter(raw);
}

export async function deleteAdminExperienceService(id: number): Promise<SafeAPIResponse<MessageResponse>> {
  const raw = await apiFetch(`/api/v1/admin/experiences/${id}`, {
    method: "DELETE",
  });
  return adminMessageResultAdapter(raw);
}

export async function listAdminProjectsService(): Promise<SafeAPIResponse<AdminProject[]>> {
  const raw = await apiFetch("/api/v1/admin/projects", {
    method: "GET",
  });
  return adminProjectsAdapter(raw);
}

export async function createAdminProjectService(payload: AdminProject): Promise<SafeAPIResponse<{ id: number }>> {
  const raw = await apiFetch("/api/v1/admin/projects", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  return adminIdResultAdapter(raw);
}

export async function updateAdminProjectService(
  id: number,
  payload: AdminProject
): Promise<SafeAPIResponse<{ id: number }>> {
  const raw = await apiFetch(`/api/v1/admin/projects/${id}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
  return adminIdResultAdapter(raw);
}

export async function deleteAdminProjectService(id: number): Promise<SafeAPIResponse<MessageResponse>> {
  const raw = await apiFetch(`/api/v1/admin/projects/${id}`, {
    method: "DELETE",
  });
  return adminMessageResultAdapter(raw);
}

export async function listAdminEducationService(): Promise<SafeAPIResponse<AdminEducation[]>> {
  const raw = await apiFetch("/api/v1/admin/education", {
    method: "GET",
  });
  return adminEducationAdapter(raw);
}

export async function createAdminEducationService(
  payload: AdminEducation
): Promise<SafeAPIResponse<{ id: number }>> {
  const raw = await apiFetch("/api/v1/admin/education", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  return adminIdResultAdapter(raw);
}

export async function updateAdminEducationService(
  id: number,
  payload: AdminEducation
): Promise<SafeAPIResponse<{ id: number }>> {
  const raw = await apiFetch(`/api/v1/admin/education/${id}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
  return adminIdResultAdapter(raw);
}

export async function deleteAdminEducationService(id: number): Promise<SafeAPIResponse<MessageResponse>> {
  const raw = await apiFetch(`/api/v1/admin/education/${id}`, {
    method: "DELETE",
  });
  return adminMessageResultAdapter(raw);
}

export async function triggerReindexService(): Promise<SafeAPIResponse<MessageResponse>> {
  const raw = await apiFetch("/api/v1/admin/reindex", {
    method: "POST",
  });
  return adminMessageResultAdapter(raw);
}

export async function getKnowledgeStatusService(): Promise<
  SafeAPIResponse<{ chunk_count: number; last_indexed_at: string | null }>
> {
  const raw = await apiFetch("/api/v1/admin/knowledge-status", {
    method: "GET",
  });
  return adminKnowledgeStatusAdapter(raw);
}

// Courses
export async function listAdminCoursesService(): Promise<SafeAPIResponse<any[]>> {
  const raw = await apiFetch("/api/v1/admin/courses", { method: "GET" });
  return { data: (raw as any)?.data || [], meta: {}, isValid: true };
}

export async function createAdminCourseService(payload: any): Promise<SafeAPIResponse<{ id: number }>> {
  const raw = await apiFetch("/api/v1/admin/courses", { method: "POST", body: JSON.stringify(payload) });
  return { data: { id: (raw as any)?.data?.id || 0 }, meta: {}, isValid: true };
}

export async function deleteAdminCourseService(id: number): Promise<SafeAPIResponse<MessageResponse>> {
  const raw = await apiFetch(`/api/v1/admin/courses/${id}`, { method: "DELETE" });
  return { data: { message: "Deleted" }, meta: {}, isValid: true };
}

// Certificates
export async function listAdminCertificatesService(): Promise<SafeAPIResponse<any[]>> {
  const raw = await apiFetch("/api/v1/admin/certificates", { method: "GET" });
  return { data: (raw as any)?.data || [], meta: {}, isValid: true };
}

export async function createAdminCertificateService(payload: any): Promise<SafeAPIResponse<{ id: number }>> {
  const raw = await apiFetch("/api/v1/admin/certificates", { method: "POST", body: JSON.stringify(payload) });
  return { data: { id: (raw as any)?.data?.id || 0 }, meta: {}, isValid: true };
}

export async function deleteAdminCertificateService(id: number): Promise<SafeAPIResponse<MessageResponse>> {
  const raw = await apiFetch(`/api/v1/admin/certificates/${id}`, { method: "DELETE" });
  return { data: { message: "Deleted" }, meta: {}, isValid: true };
}

// Social Links
export async function listAdminSocialLinksService(): Promise<SafeAPIResponse<any[]>> {
  const raw = await apiFetch("/api/v1/admin/social-links", { method: "GET" });
  return { data: (raw as any)?.data || [], meta: {}, isValid: true };
}

export async function createAdminSocialLinkService(payload: any): Promise<SafeAPIResponse<{ id: number }>> {
  const raw = await apiFetch("/api/v1/admin/social-links", { method: "POST", body: JSON.stringify(payload) });
  return { data: { id: (raw as any)?.data?.id || 0 }, meta: {}, isValid: true };
}

export async function deleteAdminSocialLinkService(id: number): Promise<SafeAPIResponse<MessageResponse>> {
  const raw = await apiFetch(`/api/v1/admin/social-links/${id}`, { method: "DELETE" });
  return { data: { message: "Deleted" }, meta: {}, isValid: true };
}

// AI Knowledge
export async function listAdminAIKnowledgeService(): Promise<SafeAPIResponse<any[]>> {
  const raw = await apiFetch("/api/v1/admin/ai-knowledge", { method: "GET" });
  return { data: (raw as any)?.data || [], meta: {}, isValid: true };
}

export async function createAdminAIKnowledgeService(payload: any): Promise<SafeAPIResponse<{ id: number }>> {
  const raw = await apiFetch("/api/v1/admin/ai-knowledge", { method: "POST", body: JSON.stringify(payload) });
  return { data: { id: (raw as any)?.data?.id || 0 }, meta: {}, isValid: true };
}

export async function deleteAdminAIKnowledgeService(id: number): Promise<SafeAPIResponse<MessageResponse>> {
  const raw = await apiFetch(`/api/v1/admin/ai-knowledge/${id}`, { method: "DELETE" });
  return { data: { message: "Deleted" }, meta: {}, isValid: true };
}
