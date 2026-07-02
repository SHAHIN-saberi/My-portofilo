import React from "react";
import { Metadata } from "next";
import {
  getProfileServer,
  getCoursesServer,
  getCertificatesServer,
} from "@/lib/serverApi";
import HomePageClient from "./HomePageClient";

export const metadata: Metadata = {
  title: "Shahin Saberi — AI Software Engineer",
  description:
    "Personal portfolio and professional profile of Shahin Saberi — AI-powered software engineer specializing in backend systems, RAG pipelines, and full-stack development.",
  openGraph: {
    title: "Shahin Saberi — AI Software Engineer",
    description:
      "Professional portfolio with AI chatbot assistant. Explore skills, projects, experience, and education.",
    type: "profile",
  },
};

// JSON-LD Structured Data for SEO
const jsonLd = {
  "@context": "https://schema.org",
  "@type": "Person",
  name: "Shahin Saberi",
  jobTitle: "AI Software Engineer",
  url: "https://shahinsaberi.com",
  sameAs: [
    "https://github.com/SHAHIN-saberi",
    "https://linkedin.com/in/shahin-saberi",
  ],
};

export default async function HomePage() {
  // Server-side fetches with ISR
  const [profile, courses, certificates] = await Promise.all([
    getProfileServer("en", 60),
    getCoursesServer("en", 60),
    getCertificatesServer("en", 60),
  ]);

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <HomePageClient
        initialProfile={profile}
        initialCourses={courses}
        initialCertificates={certificates}
      />
    </>
  );
}
