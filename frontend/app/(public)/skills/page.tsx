import React from "react";
import { Metadata } from "next";
import { getSkillsServer } from "@/lib/serverApi";
import SkillsClient from "./SkillsClient";

export const metadata: Metadata = {
  title: "Skills & Competencies",
  description:
    "Technical proficiencies, programming languages, frameworks, and tools expertise.",
};

export default async function SkillsPage() {
  // Server-side fetch with ISR (revalidate every 60 seconds)
  const initialSkills = await getSkillsServer("en", 60);

  return <SkillsClient initialSkills={initialSkills} />;
}
