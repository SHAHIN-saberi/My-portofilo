import React from "react";
import { Metadata } from "next";
import { getExperiencesServer } from "@/lib/serverApi";
import ExperienceClient from "./ExperienceClient";

export const metadata: Metadata = {
  title: "Work Experience",
  description:
    "Career trajectory, professional achievements, and work history across software engineering roles.",
};

export default async function ExperiencePage() {
  const initialExperiences = await getExperiencesServer("en", 60);

  return <ExperienceClient initialExperiences={initialExperiences} />;
}
