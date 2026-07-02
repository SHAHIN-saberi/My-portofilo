import React from "react";
import { Metadata } from "next";
import { getEducationServer } from "@/lib/serverApi";
import EducationClient from "./EducationClient";

export const metadata: Metadata = {
  title: "Education & Academic Background",
  description:
    "Degrees, institutions, certifications, and academic highlights.",
};

export default async function EducationPage() {
  const initialEducation = await getEducationServer("en", 60);

  return <EducationClient initialEducation={initialEducation} />;
}
