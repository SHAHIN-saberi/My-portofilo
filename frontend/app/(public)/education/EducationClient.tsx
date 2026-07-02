"use client";

import React, { useEffect, useState, useCallback } from "react";
import { getEducationService } from "@/services/public.service";
import { normalizeError } from "@/lib/api";
import { Education, UIStateStatus } from "@/types";
import { useLanguage } from "@/hooks/useLanguage";
import { Skeleton } from "@/components/Skeleton";
import { ErrorBanner } from "@/components/ErrorBanner";

interface EducationClientProps {
  initialEducation: Education[];
}

export default function EducationClient({ initialEducation }: EducationClientProps) {
  const { lang } = useLanguage();
  const [educationList, setEducationList] = useState<Education[]>(initialEducation);
  const [status, setStatus] = useState<UIStateStatus>(
    initialEducation.length === 0 ? "empty" : "success"
  );
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const fetchEducation = useCallback(async () => {
    setStatus("loading");
    setErrorMessage(null);
    try {
      const res = await getEducationService(lang);
      const items = res.data || [];
      setEducationList(items);
      setStatus(items.length === 0 ? "empty" : "success");
    } catch (err) {
      const normErr = normalizeError(err);
      setErrorMessage(normErr.message);
      setStatus("error");
    }
  }, [lang]);

  useEffect(() => {
    if (lang === "en" && initialEducation.length > 0) {
      return;
    }
    fetchEducation();
  }, [lang, fetchEducation, initialEducation.length]);

  return (
    <div className="max-w-4xl mx-auto px-4 py-10 space-y-8">
      <div className="border-b border-slate-200 pb-6">
        <h1 className="text-3xl font-extrabold text-slate-900">
          {lang === "fa"
            ? "سوابق تحصیلی و دانشگاهی"
            : "Education & Academic Background"}
        </h1>
        <p className="text-sm text-slate-600 mt-1">
          {lang === "fa"
            ? "مدارک تحصیلی، رشته‌ها و دانشگاه‌ها"
            : "Degrees, institutions, and academic highlights"}
        </p>
      </div>

      {status === "loading" ? (
        <Skeleton rows={3} />
      ) : status === "error" ? (
        <ErrorBanner
          message={errorMessage || "Unable to load education records"}
          onRetry={fetchEducation}
        />
      ) : status === "empty" ? (
        <div className="text-center py-12 bg-white rounded-2xl border border-slate-200 text-slate-500 font-medium">
          {lang === "fa"
            ? "سوابق تحصیلی یافت نشد."
            : "No education records listed."}
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6">
          {educationList.map((edu) => (
            <div
              key={edu.id}
              className="bg-white rounded-2xl p-6 border border-slate-200 shadow-xs space-y-3"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 pb-3">
                <div>
                  <h3 className="text-lg font-bold text-slate-900">
                    🎓 {edu.translation?.degree || "Degree"}{" "}
                    {edu.translation?.field_of_study
                      ? `in ${edu.translation.field_of_study}`
                      : ""}
                  </h3>
                  <h4 className="text-sm font-semibold text-blue-600">
                    {edu.institution || "Institution"}
                  </h4>
                </div>
                <div className="text-xs font-semibold text-slate-500 flex items-center gap-2">
                  {edu.location && <span>📍 {edu.location} |</span>}
                  <span>
                    📅 {edu.start_date || ""}{" "}
                    {edu.end_date ? `– ${edu.end_date}` : ""}
                  </span>
                </div>
              </div>
              {edu.translation?.description && (
                <p className="text-sm text-slate-700 whitespace-pre-line leading-relaxed">
                  {edu.translation.description}
                </p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
