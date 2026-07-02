"use client";

import React, { useEffect, useState, useCallback } from "react";
import { getProjectsService } from "@/services/public.service";
import { normalizeError } from "@/lib/api";
import { Project, UIStateStatus } from "@/types";
import { useLanguage } from "@/hooks/useLanguage";
import { Skeleton } from "@/components/Skeleton";
import { ErrorBanner } from "@/components/ErrorBanner";

interface ProjectsClientProps {
  initialProjects: Project[];
}

export default function ProjectsClient({ initialProjects }: ProjectsClientProps) {
  const { lang } = useLanguage();
  const [projects, setProjects] = useState<Project[]>(initialProjects);
  const [filterFeatured, setFilterFeatured] = useState<boolean | undefined>(undefined);
  const [status, setStatus] = useState<UIStateStatus>(
    initialProjects.length === 0 ? "empty" : "success"
  );
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const fetchProjects = useCallback(async () => {
    setStatus("loading");
    setErrorMessage(null);
    try {
      const res = await getProjectsService(lang, filterFeatured);
      const items = res.data || [];
      setProjects(items);
      setStatus(items.length === 0 ? "empty" : "success");
    } catch (err) {
      const normErr = normalizeError(err);
      setErrorMessage(normErr.message);
      setStatus("error");
    }
  }, [lang, filterFeatured]);

  // Re-fetch when language or filter changes
  useEffect(() => {
    if (lang === "en" && filterFeatured === undefined && initialProjects.length > 0) {
      return;
    }
    fetchProjects();
  }, [lang, filterFeatured, fetchProjects, initialProjects.length]);

  return (
    <div className="max-w-5xl mx-auto px-4 py-10 space-y-8">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-slate-200 pb-6">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-900">
            {lang === "fa" ? "پروژه‌ها" : "Projects & Portfolio"}
          </h1>
          <p className="text-sm text-slate-600 mt-1">
            {lang === "fa"
              ? "فهرست پروژه‌های توسعه‌یافته و دستاوردها"
              : "Explore featured software solutions and engineering contributions"}
          </p>
        </div>

        <div className="flex items-center gap-2 bg-slate-200 p-1 rounded-lg text-xs font-semibold">
          <button
            onClick={() => setFilterFeatured(undefined)}
            className={`px-3 py-1.5 rounded-md transition ${
              filterFeatured === undefined
                ? "bg-white text-slate-900 shadow-xs"
                : "text-slate-600 hover:text-slate-900"
            }`}
          >
            {lang === "fa" ? "همه پروژه‌ها" : "All"}
          </button>
          <button
            onClick={() => setFilterFeatured(true)}
            className={`px-3 py-1.5 rounded-md transition ${
              filterFeatured === true
                ? "bg-white text-blue-600 shadow-xs"
                : "text-slate-600 hover:text-slate-900"
            }`}
          >
            ⭐ {lang === "fa" ? "ویژه‌ها" : "Featured"}
          </button>
        </div>
      </div>

      {status === "loading" ? (
        <Skeleton rows={4} />
      ) : status === "error" ? (
        <ErrorBanner message={errorMessage || "Unable to load projects"} onRetry={fetchProjects} />
      ) : status === "empty" ? (
        <div className="text-center py-12 bg-white rounded-2xl border border-slate-200 text-slate-500 font-medium">
          {lang === "fa" ? "هیچ پروژه‌ای یافت نشد." : "No projects found matching criteria."}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {projects.map((proj) => (
            <div
              key={proj.id}
              className={`bg-white rounded-2xl p-6 border transition shadow-xs hover:shadow-md flex flex-col justify-between ${
                proj.featured ? "border-blue-300 ring-1 ring-blue-100" : "border-slate-200"
              }`}
            >
              <div className="space-y-3">
                <div className="flex items-start justify-between gap-2">
                  <h3 className="text-xl font-bold text-slate-900">
                    {proj.translation?.title || `Project #${proj.id}`}
                  </h3>
                  {proj.featured && (
                    <span className="px-2.5 py-0.5 rounded-full bg-blue-100 text-blue-800 text-xs font-bold shrink-0">
                      ⭐ Featured
                    </span>
                  )}
                </div>

                {proj.translation?.role && (
                  <p className="text-xs font-semibold text-blue-600">
                    👤 {proj.translation.role}
                  </p>
                )}

                <div className="text-xs text-slate-500 flex items-center gap-4 font-medium">
                  {proj.start_date && (
                    <span>
                      📅 {proj.start_date} {proj.end_date ? `– ${proj.end_date}` : "– Present"}
                    </span>
                  )}
                </div>

                {proj.translation?.short_description && (
                  <p className="text-sm font-medium text-slate-800 leading-relaxed">
                    {proj.translation.short_description}
                  </p>
                )}

                {proj.translation?.description && (
                  <p className="text-xs text-slate-600 leading-relaxed">
                    {proj.translation.description}
                  </p>
                )}

                {proj.translation?.impact && (
                  <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-lg text-xs text-emerald-900 font-medium space-y-1">
                    <span className="font-bold text-emerald-800">Impact / Outcome:</span>
                    <p>{proj.translation.impact}</p>
                  </div>
                )}

                {proj.tech_stack && proj.tech_stack.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 pt-2">
                    {proj.tech_stack.map((tech, idx) => (
                      <span
                        key={idx}
                        className="px-2.5 py-1 rounded-md bg-slate-100 text-slate-700 text-xs font-semibold border border-slate-200"
                      >
                        {tech}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              <div className="flex items-center gap-3 pt-6 mt-4 border-t border-slate-100">
                {proj.live_url && (
                  <a
                    href={proj.live_url}
                    target="_blank"
                    rel="noreferrer"
                    className="flex-1 text-center py-2 px-3 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold transition"
                  >
                    {lang === "fa" ? "مشاهده آنلاین" : "Live Demo"}
                  </a>
                )}
                {proj.github_url && (
                  <a
                    href={proj.github_url}
                    target="_blank"
                    rel="noreferrer"
                    className="flex-1 text-center py-2 px-3 rounded-lg bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold transition"
                  >
                    Repository
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
