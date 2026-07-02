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

export const IDENTITY_FALLBACK: IdentityModel = {
  fullName: "SHAHIN Saberi",
  nativeName: "شاهین صابری",
  title: "Full-Stack AI Engineer",
  roles: ["Backend Python Developer", "Data Engineering Specialist", "Machine Learning Engineer"],
  location: "Isfahan, Iran",
  bio: "AI-focused full-stack developer specializing in backend systems, RAG architectures, machine learning pipelines, and scalable web applications.",
  contact: {
    phone: "+989309235953",
    email: "shahin.saberi.403@gmail.com",
  },
  links: {
    github: "https://github.com/SHAHIN-saberi",
    telegram: "https://t.me/Shs84121",
    linkedin: "https://www.linkedin.com/in/shahin-saberi",
  },
};
