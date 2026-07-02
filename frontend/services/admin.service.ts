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
