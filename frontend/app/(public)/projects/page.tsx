import React from "react";
import { Metadata } from "next";
import { getProjectsServer } from "@/lib/serverApi";
import ProjectsClient from "./ProjectsClient";

export const metadata: Metadata = {
  title: "Projects & Portfolio",
  description:
    "Explore featured software solutions, engineering contributions, and technical projects.",
};

export default async function ProjectsPage() {
  // Server-side fetch with ISR (revalidate every 60 seconds)
  const initialProjects = await getProjectsServer("en", undefined, 60);

  return <ProjectsClient initialProjects={initialProjects} />;
}
