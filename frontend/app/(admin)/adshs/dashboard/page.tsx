"use client";

import React, { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import {
  getAdminProfileService,
  updateAdminProfileService,
  getKnowledgeStatusService,
  triggerReindexService,
} from "@/services/admin.service";
import { normalizeError } from "@/lib/api";
import { AdminProfile, UIState } from "@/types";
import { IDENTITY_FALLBACK } from "@/lib/identity";
import { Skeleton } from "@/components/Skeleton";
import Link from "next/link";

export default function AdminDashboardPage() {
  const router = useRouter();
  const [profile, setProfile] = useState<AdminProfile | null>(null);
  const [knowledge, setKnowledge] = useState<{ chunk_count: number; last_indexed_at: string | null } | null>(null);
  const [status, setStatus] = useState<UIState>("loading");
  const [reindexing, setReindexing] = useState(false);
  const [message, setMessage] = useState<{ text: string; type: "success" | "error" } | null>(null);

  const fetchDashboardData = useCallback(async () => {
    const token = typeof window !== "undefined" ? localStorage.getItem("admin_logged_in") === "true" : null;
    if (!token) {
      router.push("/adshs/login");
      return;
    }

    setStatus("loading");
    try {
      const [profRes, knowRes] = await Promise.all([
        getAdminProfileService("en"),
        getKnowledgeStatusService().catch(() => ({ data: { chunk_count: 0, last_indexed_at: null } })),
      ]);
      setProfile(profRes.data || null);
      setKnowledge(knowRes.data || null);
      setStatus("success");
    } catch (err: unknown) {
      const normErr = normalizeError(err);
      if (normErr.status === 401) {
        localStorage.removeItem("admin_logged_in");
        router.push("/adshs/login");
        return;
      }
      setMessage({ text: normErr.message, type: "error" });
      setStatus("error");
    }
  }, [router]);

  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  const handleReindex = async () => {
    setReindexing(true);
    setMessage(null);
    try {
      const res = await triggerReindexService();
      setMessage({ text: res.data?.message || "Reindexing triggered successfully", type: "success" });
      fetchDashboardData();
    } catch (err: unknown) {
      const normErr = normalizeError(err);
      setMessage({ text: normErr.message, type: "error" });
    } finally {
      setReindexing(false);
    }
  };

  const handleProfileSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!profile) return;
    setMessage(null);
    try {
      const res = await updateAdminProfileService(profile);
      setProfile(res.data);
      setMessage({ text: "Profile updated successfully!", type: "success" });
    } catch (err: unknown) {
      const normErr = normalizeError(err);
      setMessage({ text: normErr.message, type: "error" });
    }
  };

  if (status === "loading") {
    return (
      <div className="max-w-5xl mx-auto px-4 py-8">
        <Skeleton rows={6} />
      </div>
    );
  }

  const enTranslation = profile?.translations?.find((t) => t.lang === "en") || {
    lang: "en" as const,
    title: IDENTITY_FALLBACK.title,
    summary: "",
    bio: IDENTITY_FALLBACK.bio,
  };

  const updateTranslationField = (field: "title" | "bio" | "summary", val: string) => {
    if (!profile) return;
    const trans = profile.translations ? [...profile.translations] : [];
    const idx = trans.findIndex((t) => t.lang === "en");
    if (idx >= 0) {
      trans[idx] = { ...trans[idx], [field]: val };
    } else {
      trans.push({ lang: "en", title: IDENTITY_FALLBACK.title, summary: "", bio: IDENTITY_FALLBACK.bio, [field]: val });
    }
    setProfile({ ...profile, translations: trans });
  };

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 space-y-8">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-slate-200 pb-6">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900">⚡ Admin Dashboard (Pure Backend Runtime Source)</h1>
          <p className="text-sm text-slate-600 mt-1">
            Backend API is the sole Source of Truth.
          </p>
        </div>
      </div>

      {message && (
        <div
          className={`p-4 rounded-xl border text-sm font-semibold ${
            message.type === "success"
              ? "bg-emerald-50 border-emerald-200 text-emerald-800"
              : "bg-red-50 border-red-200 text-red-800"
          }`}
        >
          {message.text}
        </div>
      )}

      {/* Quick Navigation Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <Link
          href="/adshs/skills"
          className="p-5 bg-white border border-slate-200 rounded-xl hover:border-blue-500 hover:shadow-md transition space-y-1"
        >
          <h3 className="font-bold text-slate-900">🛠️ Manage Skills</h3>
          <p className="text-xs text-slate-500">Create, edit, or remove technical skills.</p>
        </Link>
        <Link
          href="/adshs/projects"
          className="p-5 bg-white border border-slate-200 rounded-xl hover:border-blue-500 hover:shadow-md transition space-y-1"
        >
          <h3 className="font-bold text-slate-900">🚀 Manage Projects</h3>
          <p className="text-xs text-slate-500">Add or update featured projects and tech stack.</p>
        </Link>
        <Link
          href="/adshs/experience"
          className="p-5 bg-white border border-slate-200 rounded-xl hover:border-blue-500 hover:shadow-md transition space-y-1"
        >
          <h3 className="font-bold text-slate-900">💼 Manage Experience</h3>
          <p className="text-xs text-slate-500">Update work history and roles.</p>
        </Link>
        <Link
          href="/adshs/education"
          className="p-5 bg-white border border-slate-200 rounded-xl hover:border-blue-500 hover:shadow-md transition space-y-1"
        >
          <h3 className="font-bold text-slate-900">🎓 Manage Education</h3>
          <p className="text-xs text-slate-500">Add or update academic degrees and institutions.</p>
        </Link>
      </div>

      {/* Knowledge Status & RAG Maintenance */}
      <section className="bg-slate-900 text-white rounded-2xl p-6 border border-slate-800 shadow-md flex flex-col sm:flex-row items-center justify-between gap-6">
        <div className="space-y-1 text-center sm:text-left">
          <h3 className="text-lg font-bold text-amber-400">🧠 RAG Knowledge Base Status</h3>
          <p className="text-xs text-slate-300">
            Total Indexed Chunks: <span className="font-mono font-bold text-white">{knowledge?.chunk_count || 0}</span>
          </p>
          <p className="text-xs text-slate-400">
            Last Indexed:{" "}
            <span className="font-mono">
              {knowledge?.last_indexed_at ? new Date(knowledge.last_indexed_at).toLocaleString() : "Never"}
            </span>
          </p>
        </div>
        <button
          onClick={handleReindex}
          disabled={reindexing}
          className="px-6 py-3 bg-amber-500 hover:bg-amber-600 disabled:opacity-50 text-slate-950 font-bold rounded-xl text-sm transition shadow-sm shrink-0"
        >
          {reindexing ? "Reindexing..." : "🔄 Trigger Full Reindex"}
        </button>
      </section>

      {/* Profile Editor */}
      {profile && (
        <section className="bg-white rounded-2xl p-6 border border-slate-200 shadow-xs space-y-6">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <h3 className="text-lg font-bold text-slate-900">👤 Core Profile & Bio Settings (Pure Backend CRUD)</h3>
            <span className="text-xs font-semibold text-emerald-800 bg-emerald-100 border border-emerald-300 px-2 py-0.5 rounded">
              BACKEND RUNTIME DATA
            </span>
          </div>

          <form onSubmit={handleProfileSave} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Full Name</label>
                <input
                  type="text"
                  value={profile.name || ""}
                  onChange={(e) => setProfile({ ...profile, name: e.target.value })}
                  placeholder={IDENTITY_FALLBACK.fullName}
                  className="w-full px-3 py-2 text-sm rounded-lg border border-slate-300 focus:outline-none focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Professional Title</label>
                <input
                  type="text"
                  value={enTranslation.title || ""}
                  onChange={(e) => updateTranslationField("title", e.target.value)}
                  placeholder={IDENTITY_FALLBACK.title}
                  className="w-full px-3 py-2 text-sm rounded-lg border border-slate-300 focus:outline-none focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Email</label>
                <input
                  type="email"
                  value={profile.email || ""}
                  onChange={(e) => setProfile({ ...profile, email: e.target.value })}
                  placeholder={IDENTITY_FALLBACK.contact.email}
                  className="w-full px-3 py-2 text-sm rounded-lg border border-slate-300 focus:outline-none focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Phone</label>
                <input
                  type="text"
                  value={profile.phone || ""}
                  onChange={(e) => setProfile({ ...profile, phone: e.target.value })}
                  placeholder={IDENTITY_FALLBACK.contact.phone}
                  className="w-full px-3 py-2 text-sm rounded-lg border border-slate-300 focus:outline-none focus:border-blue-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Biography (bio)</label>
              <textarea
                value={enTranslation.bio || ""}
                onChange={(e) => updateTranslationField("bio", e.target.value)}
                placeholder={IDENTITY_FALLBACK.bio}
                rows={4}
                className="w-full px-3 py-2 text-sm rounded-lg border border-slate-300 focus:outline-none focus:border-blue-500"
              />
            </div>

            <div className="flex justify-end pt-4 border-t border-slate-100">
              <button
                type="submit"
                className="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-lg text-sm transition"
              >
                Save Profile Changes
              </button>
            </div>
          </form>
        </section>
      )}
    </div>
  );
}
