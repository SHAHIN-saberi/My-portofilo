"use client";

import React, { useEffect, useState, useCallback } from "react";
import { getExperiencesService } from "@/services/public.service";
import { normalizeError } from "@/lib/api";
import { Experience, UIStateStatus } from "@/types";
import { useLanguage } from "@/hooks/useLanguage";
import { Skeleton } from "@/components/Skeleton";
import { ErrorBanner } from "@/components/ErrorBanner";

interface ExperienceClientProps {
  initialExperiences: Experience[];
}

export default function ExperienceClient({ initialExperiences }: ExperienceClientProps) {
  const { lang } = useLanguage();
  const [experiences, setExperiences] = useState<Experience[]>(initialExperiences);
  const [status, setStatus] = useState<UIStateStatus>(
    initialExperiences.length === 0 ? "empty" : "success"
  );
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const fetchExperience = useCallback(async () => {
    setStatus("loading");
    setErrorMessage(null);
    try {
      const res = await getExperiencesService(lang);
      const items = res.data || [];
      setExperiences(items);
      setStatus(items.length === 0 ? "empty" : "success");
    } catch (err) {
      const normErr = normalizeError(err);
      setErrorMessage(normErr.message);
      setStatus("error");
    }
  }, [lang]);

  useEffect(() => {
    if (lang === "en" && initialExperiences.length > 0) {
      return;
    }
    fetchExperience();
  }, [lang, fetchExperience, initialExperiences.length]);

  return (
    <div className="max-w-4xl mx-auto px-4 py-10 space-y-8">
      <div className="border-b border-slate-200 pb-6">
        <h1 className="text-3xl font-extrabold text-slate-900">
          {lang === "fa" ? "سوابق کاری و حرفه‌ای" : "Work Experience"}
        </h1>
        <p className="text-sm text-slate-600 mt-1">
          {lang === "fa"
            ? "مسیر شغلی و دستاوردهای کاری"
            : "Career trajectory and professional achievements"}
        </p>
      </div>

      {status === "loading" ? (
        <Skeleton rows={4} />
      ) : status === "error" ? (
        <ErrorBanner
          message={errorMessage || "Unable to load work experience"}
          onRetry={fetchExperience}
        />
      ) : status === "empty" ? (
        <div className="text-center py-12 bg-white rounded-2xl border border-slate-200 text-slate-500 font-medium">
          {lang === "fa"
            ? "هیچ تجربه‌ای یافت نشد."
            : "No work experience records listed."}
        </div>
      ) : (
        <div className="relative border-l-2 border-blue-200 ml-4 pl-6 space-y-8 my-6">
          {experiences.map((exp) => (
            <div
              key={exp.id}
              className="relative bg-white rounded-2xl p-6 border border-slate-200 shadow-xs"
            >
              <div className="absolute -left-[31px] top-6 w-4 h-4 rounded-full bg-blue-600 border-4 border-white shadow-xs"></div>

              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 pb-3">
                <div>
                  <h3 className="text-lg font-bold text-slate-900">
                    {exp.translation?.role || "Role"}
                  </h3>
                  <h4 className="text-sm font-semibold text-blue-600">
                    🏢 {exp.company || "Company"}
                  </h4>
                </div>

                <div className="flex items-center gap-2 text-xs font-semibold text-slate-500">
                  {exp.location && <span>📍 {exp.location} | </span>}
                  <span>
                    📅 {exp.start_date || "N/A"} –{" "}
                    {exp.is_current
                      ? lang === "fa"
                        ? "اکنون"
                        : "Present"
                      : exp.end_date || "Present"}
                  </span>
                </div>
              </div>

              {exp.translation?.description && (
                <p className="text-sm text-slate-700 mt-4 whitespace-pre-line leading-relaxed">
                  {exp.translation.description}
                </p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
