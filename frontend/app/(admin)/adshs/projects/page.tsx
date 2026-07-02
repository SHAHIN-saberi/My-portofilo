"use client";

import React, { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import {
  listAdminProjectsService,
  createAdminProjectService,
  deleteAdminProjectService,
} from "@/services/admin.service";
import { normalizeError } from "@/lib/api";
import { AdminProject, UIStateStatus } from "@/types";
import { Skeleton } from "@/components/Skeleton";

export default function AdminProjectsPage() {
  const router = useRouter();
  const [projects, setProjects] = useState<AdminProject[]>([]);
  const [status, setStatus] = useState<UIStateStatus>("loading");
  const [message, setMessage] = useState<string | null>(null);

  const [titleEn, setTitleEn] = useState("");
  const [descEn, setDescEn] = useState("");
  const [titleFa, setTitleFa] = useState("");
  const [descFa, setDescFa] = useState("");
  const [liveUrl, setLiveUrl] = useState("");
  const [githubUrl, setGithubUrl] = useState("");
  const [techStack, setTechStack] = useState("");
  const [featured, setFeatured] = useState(false);

  const fetchProjects = useCallback(async () => {
    const token = typeof window !== "undefined" ? localStorage.getItem("admin_logged_in") === "true" : null;
    if (!token) {
      router.push("/adshs/login");
      return;
    }
    setStatus("loading");
    try {
      const res = await listAdminProjectsService();
      const items = res.data || [];
      setProjects(items);
      setStatus(items.length === 0 ? "empty" : "success");
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
    fetchProjects();
  }, [fetchProjects]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!titleEn) return;
    try {
      await createAdminProjectService({
        id: 0,
        live_url: liveUrl || null,
        github_url: githubUrl || null,
        tech_stack: techStack ? techStack.split(",").map((s) => s.trim()) : [],
        featured,
        display_order: projects.length + 1,
        skill_ids: [],
        translations: [
          { lang: "en", title: titleEn, description: descEn || null },
          { lang: "fa", title: titleFa || titleEn, description: descFa || null },
        ],
      });
      setMessage("Project created successfully!");
      setTitleEn("");
      setDescEn("");
      setTitleFa("");
      setDescFa("");
      setLiveUrl("");
      setGithubUrl("");
      setTechStack("");
      setFeatured(false);
      fetchProjects();
    } catch (err: unknown) {
      const normErr = normalizeError(err);
      setMessage(normErr.message);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Are you sure you want to delete this project?")) return;
    try {
      await deleteAdminProjectService(id);
      fetchProjects();
    } catch (err: unknown) {
      const normErr = normalizeError(err);
      setMessage(normErr.message);
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 space-y-8">
      <div className="border-b border-slate-200 pb-4">
        <h1 className="text-2xl font-extrabold text-slate-900">🚀 Admin: Manage Projects</h1>
      </div>

      {message && <div className="p-3 rounded bg-blue-50 border border-blue-200 text-blue-800 text-sm">{message}</div>}

      <form onSubmit={handleCreate} className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs space-y-4">
        <h3 className="font-bold text-slate-900 border-b border-slate-100 pb-2">Add New Project</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <input
            type="text"
            placeholder="Live URL"
            value={liveUrl}
            onChange={(e) => setLiveUrl(e.target.value)}
            className="px-3 py-2 text-sm rounded border border-slate-300"
          />
          <input
            type="text"
            placeholder="GitHub URL"
            value={githubUrl}
            onChange={(e) => setGithubUrl(e.target.value)}
            className="px-3 py-2 text-sm rounded border border-slate-300"
          />
          <input
            type="text"
            placeholder="Tech Stack (comma separated)"
            value={techStack}
            onChange={(e) => setTechStack(e.target.value)}
            className="px-3 py-2 text-sm rounded border border-slate-300"
          />
        </div>
        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            id="featured"
            checked={featured}
            onChange={(e) => setFeatured(e.target.checked)}
          />
          <label htmlFor="featured" className="text-sm font-semibold text-slate-700">Featured Project</label>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <input
              type="text"
              required
              placeholder="Title (EN) *"
              value={titleEn}
              onChange={(e) => setTitleEn(e.target.value)}
              className="w-full px-3 py-2 text-sm rounded border border-slate-300"
            />
            <textarea
              placeholder="Description (EN)"
              value={descEn}
              onChange={(e) => setDescEn(e.target.value)}
              className="w-full px-3 py-2 text-sm rounded border border-slate-300 h-20"
            />
          </div>
          <div className="space-y-2">
            <input
              type="text"
              placeholder="Title (FA)"
              value={titleFa}
              onChange={(e) => setTitleFa(e.target.value)}
              className="w-full px-3 py-2 text-sm rounded border border-slate-300"
            />
            <textarea
              placeholder="Description (FA)"
              value={descFa}
              onChange={(e) => setDescFa(e.target.value)}
              className="w-full px-3 py-2 text-sm rounded border border-slate-300 h-20"
            />
          </div>
        </div>
        <button type="submit" className="px-6 py-2 bg-blue-600 text-white text-sm font-bold rounded-lg hover:bg-blue-700">
          Create Project
        </button>
      </form>

      {status === "loading" ? (
        <Skeleton rows={4} />
      ) : status === "empty" ? (
        <div className="p-8 text-center bg-white rounded-2xl border border-slate-200 text-slate-500">No projects added yet.</div>
      ) : (
        <div className="bg-white rounded-2xl border border-slate-200 divide-y divide-slate-100 overflow-hidden">
          {projects.map((proj) => (
            <div key={proj.id} className="p-4 flex items-center justify-between gap-4">
              <div>
                <h4 className="font-bold text-slate-900">
                  {proj.translations?.find((t) => t.lang === "en")?.title || `Project #${proj.id}`}
                </h4>
                <p className="text-xs text-slate-500">
                  {proj.live_url || "No link"} | {proj.featured ? "⭐ Featured" : "Standard"}
                </p>
              </div>
              <button
                onClick={() => handleDelete(proj.id)}
                className="px-3 py-1 bg-red-100 hover:bg-red-200 text-red-700 text-xs font-bold rounded"
              >
                Delete
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
