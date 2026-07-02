"use client";

import React, { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import {
  listAdminEducationService,
  createAdminEducationService,
  deleteAdminEducationService,
} from "@/services/admin.service";
import { normalizeError } from "@/lib/api";
import { AdminEducation, UIState } from "@/types";
import { Skeleton } from "@/components/Skeleton";

export default function AdminEducationPage() {
  const router = useRouter();
  const [educationList, setEducationList] = useState<AdminEducation[]>([]);
  const [status, setStatus] = useState<UIState>("loading");
  const [message, setMessage] = useState<string | null>(null);

  const [institution, setInstitution] = useState("");
  const [location, setLocation] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [degreeEn, setDegreeEn] = useState("");
  const [fieldEn, setFieldEn] = useState("");
  const [descEn, setDescEn] = useState("");
  const [degreeFa, setDegreeFa] = useState("");
  const [fieldFa, setFieldFa] = useState("");
  const [descFa, setDescFa] = useState("");

  const fetchEducation = useCallback(async () => {
    const token = typeof window !== "undefined" ? localStorage.getItem("admin_logged_in") === "true" : null;
    if (!token) {
      router.push("/adshs/login");
      return;
    }
    setStatus("loading");
    try {
      const res = await listAdminEducationService();
      const items = res.data || [];
      setEducationList(items);
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
    fetchEducation();
  }, [fetchEducation]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!institution || !degreeEn) return;
    try {
      await createAdminEducationService({
        id: 0,
        institution,
        location: location || null,
        start_date: startDate || null,
        end_date: endDate || null,
        display_order: educationList.length + 1,
        translations: [
          { lang: "en", degree: degreeEn, field_of_study: fieldEn || null, description: descEn || null },
          { lang: "fa", degree: degreeFa || degreeEn, field_of_study: fieldFa || fieldEn || null, description: descFa || null },
        ],
      });
      setMessage("Education record created successfully!");
      setInstitution("");
      setLocation("");
      setStartDate("");
      setEndDate("");
      setDegreeEn("");
      setFieldEn("");
      setDescEn("");
      setDegreeFa("");
      setFieldFa("");
      setDescFa("");
      fetchEducation();
    } catch (err: unknown) {
      const normErr = normalizeError(err);
      setMessage(normErr.message);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Are you sure you want to delete this education record?")) return;
    try {
      await deleteAdminEducationService(id);
      fetchEducation();
    } catch (err: unknown) {
      const normErr = normalizeError(err);
      setMessage(normErr.message);
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 space-y-8">
      <div className="border-b border-slate-200 pb-4">
        <h1 className="text-2xl font-extrabold text-slate-900">🎓 Admin: Manage Education</h1>
      </div>

      {message && <div className="p-3 rounded bg-blue-50 border border-blue-200 text-blue-800 text-sm">{message}</div>}

      <form onSubmit={handleCreate} className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs space-y-4">
        <h3 className="font-bold text-slate-900 border-b border-slate-100 pb-2">Add New Education Record</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <input
            type="text"
            required
            placeholder="Institution *"
            value={institution}
            onChange={(e) => setInstitution(e.target.value)}
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
            placeholder="Start Date (YYYY)"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            className="px-3 py-2 text-sm rounded border border-slate-300"
          />
          <input
            type="text"
            placeholder="End Date (YYYY)"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            className="px-3 py-2 text-sm rounded border border-slate-300"
          />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <input
              type="text"
              required
              placeholder="Degree (EN) * e.g. B.Sc."
              value={degreeEn}
              onChange={(e) => setDegreeEn(e.target.value)}
              className="w-full px-3 py-2 text-sm rounded border border-slate-300"
            />
            <input
              type="text"
              placeholder="Field of Study (EN) e.g. Computer Science"
              value={fieldEn}
              onChange={(e) => setFieldEn(e.target.value)}
              className="w-full px-3 py-2 text-sm rounded border border-slate-300"
            />
            <textarea
              placeholder="Description / Highlights (EN)"
              value={descEn}
              onChange={(e) => setDescEn(e.target.value)}
              className="w-full px-3 py-2 text-sm rounded border border-slate-300 h-20"
            />
          </div>
          <div className="space-y-2">
            <input
              type="text"
              placeholder="Degree (FA)"
              value={degreeFa}
              onChange={(e) => setDegreeFa(e.target.value)}
              className="w-full px-3 py-2 text-sm rounded border border-slate-300"
            />
            <input
              type="text"
              placeholder="Field of Study (FA)"
              value={fieldFa}
              onChange={(e) => setFieldFa(e.target.value)}
              className="w-full px-3 py-2 text-sm rounded border border-slate-300"
            />
            <textarea
              placeholder="Description / Highlights (FA)"
              value={descFa}
              onChange={(e) => setDescFa(e.target.value)}
              className="w-full px-3 py-2 text-sm rounded border border-slate-300 h-20"
            />
          </div>
        </div>
        <button type="submit" className="px-6 py-2 bg-blue-600 text-white text-sm font-bold rounded-lg hover:bg-blue-700">
          Create Education Record
        </button>
      </form>

      {status === "loading" ? (
        <Skeleton rows={4} />
      ) : status === "empty" ? (
        <div className="p-8 text-center bg-white rounded-2xl border border-slate-200 text-slate-500">No education records added yet.</div>
      ) : (
        <div className="bg-white rounded-2xl border border-slate-200 divide-y divide-slate-100 overflow-hidden">
          {educationList.map((edu) => (
            <div key={edu.id} className="p-4 flex items-center justify-between gap-4">
              <div>
                <h4 className="font-bold text-slate-900">
                  {edu.translations?.find((t) => t.lang === "en")?.degree || `Record #${edu.id}`}{" "}
                  {edu.translations?.find((t) => t.lang === "en")?.field_of_study ? `in ${edu.translations.find((t) => t.lang === "en")?.field_of_study}` : ""}
                </h4>
                <p className="text-xs text-slate-500">
                  {edu.institution} | {edu.start_date} – {edu.end_date}
                </p>
              </div>
              <button
                onClick={() => handleDelete(edu.id)}
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
