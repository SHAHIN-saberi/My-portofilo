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
        {/* Skip to main content link for keyboard/screen reader users */}
        <a
          href="#main-content"
          className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-blue-600 focus:text-white focus:rounded-lg focus:shadow-lg"
        >
          Skip to main content
        </a>
        <LanguageProvider>
          <main id="main-content" className="flex-1">
            {children}
          </main>
        </LanguageProvider>
      </body>
    </html>
  );
}
