"use client";

import React, { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { getAdminProfileService, updateAdminProfileService } from "@/services/admin.service";
import { normalizeError } from "@/lib/api";
import { AdminProfile, UIStateStatus } from "@/types";
import { Skeleton } from "@/components/Skeleton";

export default function AdminProfilePage() {
  const router = useRouter();
  const [profile, setProfile] = useState<AdminProfile | null>(null);
  const [status, setStatus] = useState<UIStateStatus>("loading");
  const [message, setMessage] = useState<string | null>(null);

  // Form fields
  const [name, setName] = useState("");
  const [photoUrl, setPhotoUrl] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [location, setLocation] = useState("");
  const [availabilityStatus, setAvailabilityStatus] = useState("");
  const [githubUrl, setGithubUrl] = useState("");
  const [linkedinUrl, setLinkedinUrl] = useState("");
  const [websiteUrl, setWebsiteUrl] = useState("");
  const [cvPdfUrl, setCvPdfUrl] = useState("");
  const [titleEn, setTitleEn] = useState("");
  const [titleFa, setTitleFa] = useState("");
  const [bioEn, setBioEn] = useState("");
  const [bioFa, setBioFa] = useState("");
  const [summaryEn, setSummaryEn] = useState("");
  const [summaryFa, setSummaryFa] = useState("");

  const fetchProfile = useCallback(async () => {
    const isLoggedIn =
      typeof window !== "undefined"
        ? localStorage.getItem("admin_logged_in") === "true"
        : null;
    if (!isLoggedIn) {
      router.push("/adshs/login");
      return;
    }
    setStatus("loading");
    try {
      const res = await getAdminProfileService("en");
      if (res.isValid && res.data) {
        setProfile(res.data);
        // Populate form
        setName(res.data.name || "");
        setPhotoUrl(res.data.photo_url || "");
        setEmail(res.data.email || "");
        setPhone(res.data.phone || "");
        setLocation(res.data.location || "");
        setAvailabilityStatus(res.data.availability_status || "");
        setGithubUrl(res.data.github_url || "");
        setLinkedinUrl(res.data.linkedin_url || "");
        setWebsiteUrl(res.data.website_url || "");
        setCvPdfUrl(res.data.cv_pdf_url || "");

        const enTrans = res.data.translations?.find((t) => t.lang === "en");
        const faTrans = res.data.translations?.find((t) => t.lang === "fa");
        setTitleEn(enTrans?.title || "");
        setTitleFa(faTrans?.title || "");
        setBioEn(enTrans?.bio || "");
        setBioFa(faTrans?.bio || "");
        setSummaryEn(enTrans?.summary || "");
        setSummaryFa(faTrans?.summary || "");
      }
      setStatus("success");
    } catch (err: unknown) {
      const normErr = normalizeError(err);
      if (normErr.status === 401) {
        localStorage.removeItem("admin_logged_in");
        router.push("/adshs/login");
        return;
      }
      setMessage(normErr.message);
      setStatus("error");
    }
  }, [router]);

  useEffect(() => {
    fetchProfile();
  }, [fetchProfile]);

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const payload: AdminProfile = {
        id: profile?.id,
        name,
        photo_url: photoUrl || null,
        email: email || null,
        phone: phone || null,
        location: location || null,
        availability_status: availabilityStatus || null,
        github_url: githubUrl || null,
        linkedin_url: linkedinUrl || null,
        website_url: websiteUrl || null,
        cv_pdf_url: cvPdfUrl || null,
        translations: [
          {
            lang: "en",
            title: titleEn || null,
            bio: bioEn || null,
            summary: summaryEn || null,
          },
          {
            lang: "fa",
            title: titleFa || null,
            bio: bioFa || null,
            summary: summaryFa || null,
          },
        ],
      };
      await updateAdminProfileService(payload);
      setMessage("Profile updated successfully!");
      fetchProfile();
    } catch (err: unknown) {
      const normErr = normalizeError(err);
      setMessage(normErr.message);
    }
  };

  if (status === "loading") {
    return (
      <div className="max-w-5xl mx-auto px-4 py-8">
        <Skeleton rows={6} />
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 space-y-8">
      <div className="border-b border-slate-200 pb-4">
        <h1 className="text-2xl font-extrabold text-slate-900">👤 Admin: Edit Profile</h1>
      </div>

      {message && (
        <div className="p-3 rounded bg-blue-50 border border-blue-200 text-blue-800 text-sm">
          {message}
        </div>
      )}

      <form onSubmit={handleUpdate} className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs space-y-6">
        <div>
          <h3 className="font-bold text-slate-900 border-b border-slate-100 pb-2 mb-4">Basic Information</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <input
              type="text"
              placeholder="Full Name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              className="px-3 py-2 text-sm rounded border border-slate-300"
            />
            <input
              type="text"
              placeholder="Photo URL"
              value={photoUrl}
              onChange={(e) => setPhotoUrl(e.target.value)}
              className="px-3 py-2 text-sm rounded border border-slate-300"
            />
            <input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="px-3 py-2 text-sm rounded border border-slate-300"
            />
            <input
              type="text"
              placeholder="Phone"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              className="px-3 py-2 text-sm rounded border border-slate-300"
            />
            <input
              type="text"
              placeholder="Location"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              className="px-3 py-2 text-sm rounded border border-slate-300"
            />
            <input
              type="text"
              placeholder="Availability Status"
              value={availabilityStatus}
              onChange={(e) => setAvailabilityStatus(e.target.value)}
              className="px-3 py-2 text-sm rounded border border-slate-300"
            />
          </div>
        </div>

        <div>
          <h3 className="font-bold text-slate-900 border-b border-slate-100 pb-2 mb-4">Social Links</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <input
              type="url"
              placeholder="GitHub URL"
              value={githubUrl}
              onChange={(e) => setGithubUrl(e.target.value)}
              className="px-3 py-2 text-sm rounded border border-slate-300"
            />
            <input
              type="url"
              placeholder="LinkedIn URL"
              value={linkedinUrl}
              onChange={(e) => setLinkedinUrl(e.target.value)}
              className="px-3 py-2 text-sm rounded border border-slate-300"
            />
            <input
              type="url"
              placeholder="Website URL"
              value={websiteUrl}
              onChange={(e) => setWebsiteUrl(e.target.value)}
              className="px-3 py-2 text-sm rounded border border-slate-300"
            />
            <input
              type="url"
              placeholder="CV PDF URL"
              value={cvPdfUrl}
              onChange={(e) => setCvPdfUrl(e.target.value)}
              className="px-3 py-2 text-sm rounded border border-slate-300"
            />
          </div>
        </div>

        <div>
          <h3 className="font-bold text-slate-900 border-b border-slate-100 pb-2 mb-4">Content (English)</h3>
          <div className="space-y-4">
            <input
              type="text"
              placeholder="Professional Title (EN)"
              value={titleEn}
              onChange={(e) => setTitleEn(e.target.value)}
              className="w-full px-3 py-2 text-sm rounded border border-slate-300"
            />
            <textarea
              placeholder="Summary (EN) - Short 1-2 sentence overview"
              value={summaryEn}
              onChange={(e) => setSummaryEn(e.target.value)}
              className="w-full px-3 py-2 text-sm rounded border border-slate-300 h-20"
            />
            <textarea
              placeholder="Bio (EN) - Detailed biography"
              value={bioEn}
              onChange={(e) => setBioEn(e.target.value)}
              className="w-full px-3 py-2 text-sm rounded border border-slate-300 h-32"
            />
          </div>
        </div>

        <div>
          <h3 className="font-bold text-slate-900 border-b border-slate-100 pb-2 mb-4">Content (Persian)</h3>
          <div className="space-y-4">
            <input
              type="text"
              placeholder="عنوان حرفه‌ای (FA)"
              value={titleFa}
              onChange={(e) => setTitleFa(e.target.value)}
              className="w-full px-3 py-2 text-sm rounded border border-slate-300"
              dir="rtl"
            />
            <textarea
              placeholder="خلاصه (FA)"
              value={summaryFa}
              onChange={(e) => setSummaryFa(e.target.value)}
              className="w-full px-3 py-2 text-sm rounded border border-slate-300 h-20"
              dir="rtl"
            />
            <textarea
              placeholder="بیوگرافی (FA)"
              value={bioFa}
              onChange={(e) => setBioFa(e.target.value)}
              className="w-full px-3 py-2 text-sm rounded border border-slate-300 h-32"
              dir="rtl"
            />
          </div>
        </div>

        <button
          type="submit"
          className="px-6 py-2 bg-blue-600 text-white text-sm font-bold rounded-lg hover:bg-blue-700"
        >
          Update Profile
        </button>
      </form>
    </div>
  );
}
