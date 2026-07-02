export type Lang = "en" | "fa";

export interface Envelope<T> {
  data: T;
  meta?: Record<string, any>;
}

export interface MessageResponse {
  message: string;
}

export interface ProfileTranslation {
  lang: Lang;
  title?: string | null;
  summary?: string | null;
  bio?: string | null;
}

export interface Profile {
  id?: number;
  name?: string | null;
  photo_url?: string | null;
  email?: string | null;
  phone?: string | null;
  location?: string | null;
  availability_status?: string | null;
  github_url?: string | null;
  linkedin_url?: string | null;
  website_url?: string | null;
  cv_pdf_url?: string | null;
  translation?: ProfileTranslation | null;
}

export interface AdminProfile extends Omit<Profile, "translation"> {
  translations?: ProfileTranslation[];
}

export interface SkillTranslation {
  lang: Lang;
  name?: string | null;
  description?: string | null;
}

export interface Skill {
  id: number;
  category?: string | null;
  proficiency?: string | null;
  years_experience?: number | null;
  display_order?: number | null;
  translation?: SkillTranslation | null;
}

export interface AdminSkill extends Omit<Skill, "translation"> {
  translations?: SkillTranslation[];
}

export interface ExperienceTranslation {
  lang: Lang;
  role?: string | null;
  description?: string | null;
}

export interface Experience {
  id: number;
  company?: string | null;
  start_date?: string | null;
  end_date?: string | null;
  is_current?: boolean | null;
  location?: string | null;
  display_order?: number | null;
  translation?: ExperienceTranslation | null;
}

export interface AdminExperience extends Omit<Experience, "translation"> {
  translations?: ExperienceTranslation[];
}

export interface ProjectTranslation {
  lang: Lang;
  title?: string | null;
  short_description?: string | null;
  description?: string | null;
  role?: string | null;
  impact?: string | null;
}

export interface Project {
  id: number;
  start_date?: string | null;
  end_date?: string | null;
  live_url?: string | null;
  github_url?: string | null;
  tech_stack?: string[] | null;
  featured?: boolean | null;
  display_order?: number | null;
  skill_ids?: number[];
  translation?: ProjectTranslation | null;
}

export interface AdminProject extends Omit<Project, "translation"> {
  translations?: ProjectTranslation[];
}

export interface EducationTranslation {
  lang: Lang;
  degree?: string | null;
  field_of_study?: string | null;
  description?: string | null;
}

export interface Education {
  id: number;
  institution?: string | null;
  start_date?: string | null;
  end_date?: string | null;
  location?: string | null;
  display_order?: number | null;
  translation?: EducationTranslation | null;
}

export interface AdminEducation extends Omit<Education, "translation"> {
  translations?: EducationTranslation[];
}

export interface CourseTranslation {
  lang: Lang;
  title?: string | null;
  description?: string | null;
}

export interface Course {
  id: number;
  provider?: string | null;
  completion_date?: string | null;
  credential_url?: string | null;
  display_order?: number | null;
  translation?: CourseTranslation | null;
}

export interface CertificateTranslation {
  lang: Lang;
  title?: string | null;
  description?: string | null;
}

export interface Certificate {
  id: number;
  issuer?: string | null;
  issue_date?: string | null;
  credential_url?: string | null;
  display_order?: number | null;
  translation?: CertificateTranslation | null;
}

export interface SocialLink {
  id: number;
  platform?: string | null;
  url?: string | null;
  display_order?: number | null;
  is_visible?: boolean | null;
}

export interface ChatSource {
  source_type: string;
  source_id: number;
  score: number;
}

export interface ChatQueryResponse {
  answer: string;
  status: "answered" | "unrelated" | "no_answer" | "error" | "needs_clarification";
  sources?: ChatSource[] | null;
}

export interface TokenResponse {
  access_token: string;
  expires_in_minutes: number;
}

export * from "./state";
export * from "./safe";
