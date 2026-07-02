"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useLanguage } from "@/hooks/useLanguage";
import { IDENTITY_FALLBACK } from "@/lib/identity";
import { getProfileService } from "@/services/public.service";

export const Navbar: React.FC = () => {
  const pathname = usePathname();
  const { lang, setLang } = useLanguage();
  const [name, setName] = useState<string>(
    lang === "fa" ? IDENTITY_FALLBACK.nativeName : IDENTITY_FALLBACK.fullName
  );
  const [title, setTitle] = useState<string>(IDENTITY_FALLBACK.title);

  useEffect(() => {
    let mounted = true;
    getProfileService(lang)
      .then((res) => {
        if (mounted && res.isValid && res.data) {
          const backendName = res.data.name;
          const backendTitle = res.data.translation?.title;
          setName(backendName ?? (lang === "fa" ? IDENTITY_FALLBACK.nativeName : IDENTITY_FALLBACK.fullName));
          setTitle(backendTitle ?? IDENTITY_FALLBACK.title);
        }
      })
      .catch(() => {
        // Emergency fallback remains
      });
    return () => {
      mounted = false;
    };
  }, [lang]);

  const links = [
    { href: "/", labelEn: "Home", labelFa: "خانه" },
    { href: "/projects", labelEn: "Projects", labelFa: "پروژه‌ها" },
    { href: "/skills", labelEn: "Skills", labelFa: "مهارت‌ها" },
    { href: "/experience", labelEn: "Experience", labelFa: "تجربیات" },
    { href: "/education", labelEn: "Education", labelFa: "تحصیلات" },
    { href: "/chat", labelEn: "AI Chat", labelFa: "چت هوش مصنوعی" },
  ];

  if (pathname?.startsWith("/adshs")) {
    return null;
  }

  return (
    <nav className="bg-slate-900 text-white shadow-md sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-4 py-3 flex flex-wrap items-center justify-between gap-4">
        <Link href="/" className="flex flex-col group">
          <span className="text-lg font-bold tracking-tight group-hover:text-blue-400 transition">
            {name}
          </span>
          <span className="text-[11px] font-medium text-slate-400 group-hover:text-slate-300">
            {title}
          </span>
        </Link>

        <div className="flex flex-wrap items-center gap-6 text-sm font-medium">
          {links.map((link) => {
            const isActive = pathname === link.href;
            return (
              <Link
                key={link.href}
                href={link.href}
                className={`transition pb-1 border-b-2 ${
                  isActive ? "border-blue-400 text-blue-400 font-bold" : "border-transparent hover:text-slate-300"
                }`}
              >
                {lang === "fa" ? link.labelFa : link.labelEn}
              </Link>
            );
          })}
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setLang(lang === "en" ? "fa" : "en")}
            className="px-3 py-1 text-xs font-semibold rounded bg-slate-800 hover:bg-slate-700 border border-slate-700 transition"
          >
            {lang === "en" ? "🇮🇷 فارسی (FA)" : "🇺🇸 English (EN)"}
          </button>
        </div>
      </div>
    </nav>
  );
};
