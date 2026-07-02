"use client";

import React, { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import {
  listAdminSkillsService,
  createAdminSkillService,
  deleteAdminSkillService,
} from "@/services/admin.service";
import { normalizeError } from "@/lib/api";
import { AdminSkill, UIStateStatus } from "@/types";
import { Skeleton } from "@/components/Skeleton";

export default function AdminSkillsPage() {
  const router = useRouter();
  const [skills, setSkills] = useState<AdminSkill[]>([]);
  const [status, setStatus] = useState<UIStateStatus>("loading");
  const [message, setMessage] = useState<string | null>(null);

  const [category, setCategory] = useState("");
  const [proficiency, setProficiency] = useState("");
  const [years, setYears] = useState("");
  const [nameEn, setNameEn] = useState("");
  const [descEn, setDescEn] = useState("");
  const [nameFa, setNameFa] = useState("");
  const [descFa, setDescFa] = useState("");

  const fetchSkills = useCallback(async () => {
    const token = typeof window !== "undefined" ? localStorage.getItem("admin_logged_in") === "true" : null;
    if (!token) {
      router.push("/adshs/login");
      return;
    }
    setStatus("loading");
    try {
      const res = await listAdminSkillsService();
      const items = res.data || [];
      setSkills(items);
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
    fetchSkills();
  }, [fetchSkills]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!nameEn) return;
    try {
      await createAdminSkillService({
        id: 0,
        category: category || null,
        proficiency: proficiency || null,
        years_experience: years ? parseFloat(years) : null,
        display_order: skills.length + 1,
        translations: [
          { lang: "en", name: nameEn, description: descEn || null },
          { lang: "fa", name: nameFa || nameEn, description: descFa || null },
        ],
      });
      setMessage("Skill created successfully!");
      setNameEn("");
      setDescEn("");
      setNameFa("");
      setDescFa("");
      setCategory("");
      setProficiency("");
      setYears("");
      fetchSkills();
    } catch (err: unknown) {
      const normErr = normalizeError(err);
      setMessage(normErr.message);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Are you sure you want to delete this skill?")) return;
    try {
      await deleteAdminSkillService(id);
      fetchSkills();
    } catch (err: unknown) {
      const normErr = normalizeError(err);
      setMessage(normErr.message);
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 space-y-8">
      <div className="border-b border-slate-200 pb-4">
        <h1 className="text-2xl font-extrabold text-slate-900">🛠️ Admin: Manage Skills</h1>
      </div>

      {message && <div className="p-3 rounded bg-blue-50 border border-blue-200 text-blue-800 text-sm">{message}</div>}

      <form onSubmit={handleCreate} className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs space-y-4">
        <h3 className="font-bold text-slate-900 border-b border-slate-100 pb-2">Add New Skill</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <input
            type="text"
            placeholder="Category (e.g. Frontend)"
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="px-3 py-2 text-sm rounded border border-slate-300"
          />
          <input
            type="text"
            placeholder="Proficiency (e.g. Expert)"
            value={proficiency}
            onChange={(e) => setProficiency(e.target.value)}
            className="px-3 py-2 text-sm rounded border border-slate-300"
          />
          <input
            type="number"
            step="0.5"
            placeholder="Years of Experience"
            value={years}
            onChange={(e) => setYears(e.target.value)}
            className="px-3 py-2 text-sm rounded border border-slate-300"
          />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <input
              type="text"
              required
              placeholder="Name (EN) *"
              value={nameEn}
              onChange={(e) => setNameEn(e.target.value)}
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
              placeholder="Name (FA)"
              value={nameFa}
              onChange={(e) => setNameFa(e.target.value)}
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
          Create Skill
        </button>
      </form>

      {status === "loading" ? (
        <Skeleton rows={4} />
      ) : status === "empty" ? (
        <div className="p-8 text-center bg-white rounded-2xl border border-slate-200 text-slate-500">No skills added yet.</div>
      ) : (
        <div className="bg-white rounded-2xl border border-slate-200 divide-y divide-slate-100 overflow-hidden">
          {skills.map((skill) => (
            <div key={skill.id} className="p-4 flex items-center justify-between gap-4">
              <div>
                <h4 className="font-bold text-slate-900">
                  {skill.translations?.find((t) => t.lang === "en")?.name || `Skill #${skill.id}`}
                </h4>
                <p className="text-xs text-slate-500">
                  {skill.category} | {skill.proficiency} | {skill.years_experience} yrs
                </p>
              </div>
              <button
                onClick={() => handleDelete(skill.id)}
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
