"use client";

import React, { useEffect, useState, useCallback } from "react";
import { getProfileService, getCoursesService, getCertificatesService } from "@/services/public.service";
import { normalizeError } from "@/lib/api";
import { Certificate, Course, Profile, UIState } from "@/types";
import { useLanguage } from "@/hooks/useLanguage";
import { Skeleton } from "@/components/Skeleton";
import { ErrorBanner } from "@/components/ErrorBanner";
import { IDENTITY_FALLBACK } from "@/lib/identity";
import Link from "next/link";

interface HomePageClientProps {
  initialProfile: Profile | null;
  initialCourses: Course[];
  initialCertificates: Certificate[];
}

export default function HomePageClient({
  initialProfile,
  initialCourses,
  initialCertificates,
}: HomePageClientProps) {
  const { lang } = useLanguage();
  const [profile, setProfile] = useState<Profile | null>(initialProfile);
  const [courses, setCourses] = useState<Course[]>(initialCourses);
  const [certificates, setCertificates] = useState<Certificate[]>(initialCertificates);

  const [status, setStatus] = useState<UIState>("success");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setStatus("loading");
    setErrorMessage(null);
    try {
      const [profileRes, coursesRes, certsRes] = await Promise.all([
        getProfileService(lang).catch(() => ({ data: null, isValid: false })),
        getCoursesService(lang).catch(() => ({ data: [], isValid: false })),
        getCertificatesService(lang).catch(() => ({ data: [], isValid: false })),
      ]);
      if (profileRes.isValid && profileRes.data) {
        setProfile(profileRes.data);
      } else {
        setProfile(null);
      }
      setCourses(coursesRes.data || []);
      setCertificates(certsRes.data || []);
      setStatus("success");
    } catch (err) {
      const normErr = normalizeError(err);
      setErrorMessage(normErr.message);
      setStatus("error");
    }
  }, [lang]);

  // Re-fetch when language changes (skip initial render for English)
  useEffect(() => {
    if (lang === "en" && initialProfile) {
      return;
    }
    fetchData();
  }, [lang, fetchData, initialProfile]);

  if (status === "loading") {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <Skeleton rows={4} />
      </div>
    );
  }

  if (status === "error") {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <ErrorBanner message={errorMessage || "Unable to load content"} onRetry={fetchData} />
      </div>
    );
  }

  // Field-Level Fallback ONLY (backend ?? emergency fallback)
  const name = profile?.name ?? (lang === "fa" ? IDENTITY_FALLBACK.nativeName : IDENTITY_FALLBACK.fullName);
  const title = profile?.translation?.title ?? IDENTITY_FALLBACK.title;
  const bio = profile?.translation?.bio ?? IDENTITY_FALLBACK.bio;
  const location = profile?.location ?? IDENTITY_FALLBACK.location;
  const phone = profile?.phone ?? IDENTITY_FALLBACK.contact.phone;
  const email = profile?.email ?? IDENTITY_FALLBACK.contact.email;
  const photoUrl = profile?.photo_url;
  const availStatus = profile?.availability_status ?? (lang === "fa" ? "آماده همکاری" : "Available for Opportunities");

  const github = profile?.github_url ?? IDENTITY_FALLBACK.links.github;
  const linkedin = profile?.linkedin_url ?? IDENTITY_FALLBACK.links.linkedin;
  const telegram = IDENTITY_FALLBACK.links.telegram;
  const website = profile?.website_url;
  const cv = profile?.cv_pdf_url;

  return (
    <div className="max-w-4xl mx-auto px-4 py-10 space-y-12">
      {/* Hero Section */}
      <section className="bg-white rounded-2xl p-8 border border-slate-200 shadow-sm flex flex-col md:flex-row items-center gap-8">
        {photoUrl ? (
          <img src={photoUrl} alt={name} className="w-32 h-32 rounded-full object-cover border-4 border-slate-100 shadow-md" />
        ) : (
          <div className="w-32 h-32 rounded-full bg-slate-900 text-white flex items-center justify-center text-3xl font-extrabold shadow-md">
            {name.charAt(0)}
          </div>
        )}

        <div className="flex-1 space-y-3 text-center md:text-left">
          <div className="flex flex-wrap items-center justify-center md:justify-start gap-3">
            <h1 className="text-3xl font-extrabold text-slate-900">{name}</h1>
            <span className="px-3 py-1 text-xs font-semibold rounded-full bg-emerald-100 text-emerald-800 border border-emerald-200">
              {availStatus}
            </span>
          </div>

          <h2 className="text-xl font-bold text-blue-600">{title}</h2>

          <div className="flex flex-wrap items-center justify-center md:justify-start gap-1.5 pt-1">
            {IDENTITY_FALLBACK.roles.map((role, idx) => (
              <span
                key={idx}
                className="px-2.5 py-0.5 rounded bg-slate-100 text-slate-700 text-xs font-semibold border border-slate-200"
              >
                🛠️ {role}
              </span>
            ))}
          </div>

          <div className="flex flex-wrap items-center justify-center md:justify-start gap-4 text-xs font-medium text-slate-500 pt-2">
            <span>📍 {location}</span>
            {email && (
              <a href={`mailto:${email}`} className="hover:text-blue-600 transition">
                ✉️ {email}
              </a>
            )}
            {phone && <span>📞 {phone}</span>}
          </div>

          <div className="flex flex-wrap items-center justify-center md:justify-start gap-3 pt-4">
            {github && (
              <a
                href={github}
                target="_blank"
                rel="noreferrer"
                className="px-4 py-2 rounded-lg bg-slate-900 text-white text-sm font-semibold hover:bg-slate-800 transition shadow-xs"
              >
                GitHub
              </a>
            )}
            {linkedin && (
              <a
                href={linkedin}
                target="_blank"
                rel="noreferrer"
                className="px-4 py-2 rounded-lg bg-blue-600 text-white text-sm font-semibold hover:bg-blue-700 transition shadow-xs"
              >
                LinkedIn
              </a>
            )}
            {telegram && (
              <a
                href={telegram}
                target="_blank"
                rel="noreferrer"
                className="px-4 py-2 rounded-lg bg-sky-500 text-white text-sm font-semibold hover:bg-sky-600 transition shadow-xs"
              >
                Telegram
              </a>
            )}
            {website && (
              <a
                href={website}
                target="_blank"
                rel="noreferrer"
                className="px-4 py-2 rounded-lg bg-slate-100 text-slate-800 text-sm font-semibold hover:bg-slate-200 border border-slate-300 transition"
              >
                Website
              </a>
            )}
            {cv && (
              <a
                href={cv}
                target="_blank"
                rel="noreferrer"
                className="px-4 py-2 rounded-lg bg-amber-500 text-white text-sm font-semibold hover:bg-amber-600 transition shadow-xs"
              >
                {lang === "fa" ? "دانلود رزومه (CV)" : "Download CV"}
              </a>
            )}
            <Link
              href="/chat"
              className="px-4 py-2 rounded-lg bg-gradient-to-r from-purple-600 to-indigo-600 text-white text-sm font-semibold hover:from-purple-700 hover:to-indigo-700 transition shadow-xs"
            >
              💬 {lang === "fa" ? "گفتگو با هوش مصنوعی" : "Ask AI Assistant"}
            </Link>
          </div>
        </div>
      </section>

      {/* About Section */}
      {bio && (
        <section className="bg-white rounded-2xl p-8 border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <h3 className="text-xl font-bold text-slate-900">
              {lang === "fa" ? "درباره من" : "Biography & Overview"}
            </h3>
            <span className="text-[11px] font-mono bg-slate-100 px-2 py-0.5 rounded text-slate-600 border">
              Backend Runtime Data
            </span>
          </div>
          <p className="text-slate-700 whitespace-pre-line leading-relaxed text-base">{bio}</p>
        </section>
      )}

      {/* Courses Section */}
      {courses.length > 0 && (
        <section className="bg-white rounded-2xl p-8 border border-slate-200 shadow-sm space-y-6">
          <h3 className="text-xl font-bold text-slate-900 border-b border-slate-100 pb-3">
            {lang === "fa" ? "دوره‌ها و آموزش‌ها" : "Courses & Training"}
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {courses.map((course) => (
              <div key={course.id} className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-2">
                <h4 className="font-bold text-slate-900">{course.translation?.title || "Course"}</h4>
                <div className="flex items-center justify-between text-xs text-slate-500 font-medium">
                  <span>🏢 {course.provider || "N/A"}</span>
                  {course.completion_date && <span>📅 {course.completion_date}</span>}
                </div>
                {course.translation?.description && (
                  <p className="text-xs text-slate-600">{course.translation.description}</p>
                )}
                {course.credential_url && (
                  <a
                    href={course.credential_url}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-block text-xs font-semibold text-blue-600 hover:underline pt-1"
                  >
                    {lang === "fa" ? "مشاهده گواهی →" : "View Credential →"}
                  </a>
                )}
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Certificates Section */}
      {certificates.length > 0 && (
        <section className="bg-white rounded-2xl p-8 border border-slate-200 shadow-sm space-y-6">
          <h3 className="text-xl font-bold text-slate-900 border-b border-slate-100 pb-3">
            {lang === "fa" ? "گواهینامه‌ها" : "Certificates"}
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {certificates.map((cert) => (
              <div key={cert.id} className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-2">
                <h4 className="font-bold text-slate-900">{cert.translation?.title || "Certificate"}</h4>
                <div className="flex items-center justify-between text-xs text-slate-500 font-medium">
                  <span>🏅 {cert.issuer || "N/A"}</span>
                  {cert.issue_date && <span>📅 {cert.issue_date}</span>}
                </div>
                {cert.translation?.description && (
                  <p className="text-xs text-slate-600">{cert.translation.description}</p>
                )}
                {cert.credential_url && (
                  <a
                    href={cert.credential_url}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-block text-xs font-semibold text-blue-600 hover:underline pt-1"
                  >
                    {lang === "fa" ? "مشاهده گواهینامه →" : "Verify Certificate →"}
                  </a>
                )}
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
