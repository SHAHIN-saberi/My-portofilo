"use client";

import React, { useEffect, useState, useCallback } from "react";
import { getSkillsService } from "@/services/public.service";
import { normalizeError } from "@/lib/api";
import { Skill, UIStateStatus } from "@/types";
import { useLanguage } from "@/hooks/useLanguage";
import { Skeleton } from "@/components/Skeleton";
import { ErrorBanner } from "@/components/ErrorBanner";

interface SkillsClientProps {
  initialSkills: Skill[];
}

export default function SkillsClient({ initialSkills }: SkillsClientProps) {
  const { lang } = useLanguage();
  const [skills, setSkills] = useState<Skill[]>(initialSkills);
  const [categoryFilter, setCategoryFilter] = useState<string>("");
  const [status, setStatus] = useState<UIStateStatus>(
    initialSkills.length === 0 ? "empty" : "success"
  );
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const fetchSkills = useCallback(async () => {
    setStatus("loading");
    setErrorMessage(null);
    try {
      const res = await getSkillsService(lang, categoryFilter || undefined);
      const items = res.data || [];
      setSkills(items);
      setStatus(items.length === 0 ? "empty" : "success");
    } catch (err) {
      const normErr = normalizeError(err);
      setErrorMessage(normErr.message);
      setStatus("error");
    }
  }, [lang, categoryFilter]);

  // Re-fetch when language or filter changes
  useEffect(() => {
    // Skip initial render if we already have data for the default language
    if (lang === "en" && !categoryFilter && initialSkills.length > 0) {
      return;
    }
    fetchSkills();
  }, [lang, categoryFilter, fetchSkills, initialSkills.length]);

  return (
    <div className="max-w-4xl mx-auto px-4 py-10 space-y-8">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-slate-200 pb-6">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-900">
            {lang === "fa" ? "مهارت‌های فنی و تخصصی" : "Skills & Competencies"}
          </h1>
          <p className="text-sm text-slate-600 mt-1">
            {lang === "fa"
              ? "تخصص‌ها، زبان‌های برنامه‌نویسی و ابزارها"
              : "Technical proficiencies and tools overview"}
          </p>
        </div>

        <div className="flex items-center gap-2">
          <input
            type="text"
            placeholder={lang === "fa" ? "جستجو دسته‌بندی..." : "Filter category..."}
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="px-3 py-1.5 text-xs rounded-lg border border-slate-300 focus:outline-none focus:border-blue-500 bg-white"
          />
          {categoryFilter && (
            <button
              onClick={() => setCategoryFilter("")}
              className="text-xs text-slate-500 hover:text-slate-800 underline"
            >
              Clear
            </button>
          )}
        </div>
      </div>

      {status === "loading" ? (
        <Skeleton rows={5} />
      ) : status === "error" ? (
        <ErrorBanner message={errorMessage || "Unable to load skills"} onRetry={fetchSkills} />
      ) : status === "empty" ? (
        <div className="text-center py-12 bg-white rounded-2xl border border-slate-200 text-slate-500 font-medium">
          {lang === "fa" ? "مهارتی در این دسته‌بندی یافت نشد." : "No skills found matching filter."}
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
          {skills.map((skill) => (
            <div
              key={skill.id}
              className="bg-white rounded-xl p-5 border border-slate-200 shadow-xs hover:shadow-sm transition space-y-2 flex flex-col justify-between"
            >
              <div>
                <div className="flex items-start justify-between gap-2">
                  <h3 className="font-bold text-slate-900 text-base">
                    {skill.translation?.name || `Skill #${skill.id}`}
                  </h3>
                  {skill.proficiency && (
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-blue-50 text-blue-700 border border-blue-200 shrink-0">
                      {skill.proficiency}
                    </span>
                  )}
                </div>
                {skill.category && (
                  <span className="inline-block text-xs font-semibold text-slate-500 mt-1">
                    🏷️ {skill.category}
                  </span>
                )}
                {skill.translation?.description && (
                  <p className="text-xs text-slate-600 mt-2 leading-relaxed">
                    {skill.translation.description}
                  </p>
                )}
              </div>

              {skill.years_experience !== null && skill.years_experience !== undefined && (
                <div className="pt-3 mt-2 border-t border-slate-100 text-xs font-semibold text-slate-700 flex items-center justify-between">
                  <span>Experience:</span>
                  <span className="text-blue-600 font-bold">
                    {skill.years_experience}+ years
                  </span>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
