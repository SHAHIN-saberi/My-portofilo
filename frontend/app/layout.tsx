import "../styles/globals.css";
import React from "react";
import type { Metadata } from "next";
import { LanguageProvider } from "@/hooks/useLanguage";

export const metadata: Metadata = {
  title: "SHAHIN | Portfolio",
  description: "Bilingual professional profile driven by Next.js and contract-driven API layer.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen flex flex-col bg-slate-50 text-slate-900">
        <LanguageProvider>{children}</LanguageProvider>
      </body>
    </html>
  );
}
