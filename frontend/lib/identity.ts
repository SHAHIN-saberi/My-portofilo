// Identity fallback configuration
// In production, these values should come from environment variables or API
// For development/demo, hardcoded values are acceptable

export interface IdentityModel {
  fullName: string;
  nativeName: string;
  title: string;
  roles: string[];
  location: string;
  bio: string;
  contact: {
    phone: string;
    email: string;
  };
  links: {
    github: string;
    telegram: string;
    linkedin: string;
  };
}

// Load from environment variables if available, otherwise use demo values
// In production, set these via NEXT_PUBLIC_* env vars or fetch from API
export const IDENTITY_FALLBACK: IdentityModel = {
  fullName: process.env.NEXT_PUBLIC_OWNER_NAME || "SHAHIN Saberi",
  nativeName: process.env.NEXT_PUBLIC_OWNER_NAME_NATIVE || "شاهین صابری",
  title: process.env.NEXT_PUBLIC_OWNER_TITLE || "Full-Stack AI Engineer",
  roles: (process.env.NEXT_PUBLIC_OWNER_ROLES || "Backend Python Developer,Data Engineering Specialist,Machine Learning Engineer").split(","),
  location: process.env.NEXT_PUBLIC_OWNER_LOCATION || "Isfahan, Iran",
  bio: process.env.NEXT_PUBLIC_OWNER_BIO || "AI-focused full-stack developer specializing in backend systems, RAG architectures, machine learning pipelines, and scalable web applications.",
  contact: {
    phone: process.env.NEXT_PUBLIC_OWNER_PHONE || "", // Empty by default for privacy
    email: process.env.NEXT_PUBLIC_OWNER_EMAIL || "", // Empty by default for privacy
  },
  links: {
    github: process.env.NEXT_PUBLIC_GITHUB_URL || "https://github.com/SHAHIN-saberi",
    telegram: process.env.NEXT_PUBLIC_TELEGRAM_URL || "", // Empty by default for privacy
    linkedin: process.env.NEXT_PUBLIC_LINKEDIN_URL || "https://www.linkedin.com/in/shahin-saberi",
  },
};
