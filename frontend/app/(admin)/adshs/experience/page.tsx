"use client";

import React, { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import {
  listAdminExperiencesService,
  createAdminExperienceService,
  deleteAdminExperienceService,
} from "@/services/admin.service";
import { normalizeError } from "@/lib/api";
import { AdminExperience, UIStateStatus } from "@/types";
import { Skeleton } from "@/components/Skeleton";

export default function AdminExperiencePage() {
  const router = useRouter();
  const [experiences, setExperiences] = useState<AdminExperience[]>([]);
  const [status, setStatus] = useState<UIStateStatus>("loading");
  const [message, setMessage] = useState<string | null>(null);

  const [company, setCompany] = useState("");
  const [location, setLocation] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [isCurrent, setIsCurrent] = useState(false);
  const [roleEn, setRoleEn] = useState("");
  const [descEn, setDescEn] = useState("");
  const [roleFa, setRoleFa] = useState("");
  const [descFa, setDescFa] = useState("");

  const fetchExperience = useCallback(async () => {
    const token = typeof window !== "undefined" ? localStorage.getItem("admin_logged_in") === "true" : null;
    if (!token) {
      router.push("/adshs/login");
      return;
    }
    setStatus("loading");
    try {
      const res = await listAdminExperiencesService();
      const items = res.data || [];
      setExperiences(items);
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
    fetchExperience();
  }, [fetchExperience]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!roleEn || !company) return;
    try {
      await createAdminExperienceService({
        id: 0,
        company,
        location: location || null,
        start_date: startDate || null,
        end_date: isCurrent ? null : endDate || null,
        is_current: isCurrent,
        display_order: experiences.length + 1,
        translations: [
          { lang: "en", role: roleEn, description: descEn || null },
          { lang: "fa", role: roleFa || roleEn, description: descFa || null },
        ],
      });
      setMessage("Experience created successfully!");
      setCompany("");
      setLocation("");
      setStartDate("");
      setEndDate("");
      setIsCurrent(false);
      setRoleEn("");
      setDescEn("");
      setRoleFa("");
      setDescFa("");
      fetchExperience();
    } catch (err: unknown) {
      const normErr = normalizeError(err);
      setMessage(normErr.message);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Are you sure you want to delete this experience?")) return;
    try {
      await deleteAdminExperienceService(id);
      fetchExperience();
    } catch (err: unknown) {
      const normErr = normalizeError(err);
      setMessage(normErr.message);
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 space-y-8">
      <div className="border-b border-slate-200 pb-4">
        <h1 className="text-2xl font-extrabold text-slate-900">💼 Admin: Manage Experience</h1>
      </div>

      {message && <div className="p-3 rounded bg-blue-50 border border-blue-200 text-blue-800 text-sm">{message}</div>}

      <form onSubmit={handleCreate} className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs space-y-4">
        <h3 className="font-bold text-slate-900 border-b border-slate-100 pb-2">Add New Experience</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <input
            type="text"
            required
            placeholder="Company *"
            value={company}
            onChange={(e) => setCompany(e.target.value)}
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
            placeholder="Start Date (YYYY-MM)"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            className="px-3 py-2 text-sm rounded border border-slate-300"
          />
          <input
            type="text"
            disabled={isCurrent}
            placeholder="End Date (YYYY-MM)"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            className="px-3 py-2 text-sm rounded border border-slate-300 disabled:bg-slate-100"
          />
        </div>
        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            id="isCurrent"
            checked={isCurrent}
            onChange={(e) => setIsCurrent(e.target.checked)}
          />
          <label htmlFor="isCurrent" className="text-sm font-semibold text-slate-700">Current Role</label>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <input
              type="text"
              required
              placeholder="Role (EN) *"
              value={roleEn}
              onChange={(e) => setRoleEn(e.target.value)}
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
              placeholder="Role (FA)"
              value={roleFa}
              onChange={(e) => setRoleFa(e.target.value)}
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
          Create Experience
        </button>
      </form>

      {status === "loading" ? (
        <Skeleton rows={4} />
      ) : status === "empty" ? (
        <div className="p-8 text-center bg-white rounded-2xl border border-slate-200 text-slate-500">No work experience added yet.</div>
      ) : (
        <div className="bg-white rounded-2xl border border-slate-200 divide-y divide-slate-100 overflow-hidden">
          {experiences.map((exp) => (
            <div key={exp.id} className="p-4 flex items-center justify-between gap-4">
              <div>
                <h4 className="font-bold text-slate-900">
                  {exp.translations?.find((t) => t.lang === "en")?.role || `Role #${exp.id}`}
                </h4>
                <p className="text-xs text-slate-500">
                  {exp.company} | {exp.start_date} – {exp.is_current ? "Present" : exp.end_date}
                </p>
              </div>
              <button
                onClick={() => handleDelete(exp.id)}
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
