"use client";

import React, { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { normalizeError } from "@/lib/api";
import { UIStateStatus } from "@/types";
import { Skeleton } from "@/components/Skeleton";

export interface CrudField {
  key: string;
  label: string;
  type?: "text" | "number" | "textarea" | "date";
  required?: boolean;
  placeholder?: string;
}

export interface CrudColumn {
  key: string;
  label: string;
  render?: (item: any) => React.ReactNode;
}

interface AdminCrudPageProps {
  title: string;
  icon?: string;
  fields: CrudField[];
  columns: CrudColumn[];
  listService: () => Promise<any>;
  createService: (payload: any) => Promise<any>;
  deleteService: (id: number) => Promise<any>;
  getItemTitle: (item: any) => string;
  buildPayload: (formData: Record<string, string>) => any;
}

export default function AdminCrudPage({
  title,
  icon = "📋",
  fields,
  columns,
  listService,
  createService,
  deleteService,
  getItemTitle,
  buildPayload,
}: AdminCrudPageProps) {
  const router = useRouter();
  const [items, setItems] = useState<any[]>([]);
  const [status, setStatus] = useState<UIStateStatus>("loading");
  const [message, setMessage] = useState<string | null>(null);
  const [formData, setFormData] = useState<Record<string, string>>({});

  const fetchItems = useCallback(async () => {
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
      const res = await listService();
      const data = res.data || [];
      setItems(data);
      setStatus(data.length === 0 ? "empty" : "success");
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
  }, [router, listService]);

  useEffect(() => {
    fetchItems();
  }, [fetchItems]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const payload = buildPayload(formData);
      await createService(payload);
      setMessage("Created successfully!");
      setFormData({});
      fetchItems();
    } catch (err: unknown) {
      const normErr = normalizeError(err);
      setMessage(normErr.message);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Are you sure you want to delete this item?")) return;
    try {
      await deleteService(id);
      fetchItems();
    } catch (err: unknown) {
      const normErr = normalizeError(err);
      setMessage(normErr.message);
    }
  };

  const updateField = (key: string, value: string) => {
    setFormData((prev) => ({ ...prev, [key]: value }));
  };

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 space-y-8">
      <div className="border-b border-slate-200 pb-4">
        <h1 className="text-2xl font-extrabold text-slate-900">
          {icon} Admin: {title}
        </h1>
      </div>

      {message && (
        <div className="p-3 rounded bg-blue-50 border border-blue-200 text-blue-800 text-sm">
          {message}
        </div>
      )}

      <form
        onSubmit={handleCreate}
        className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs space-y-4"
      >
        <h3 className="font-bold text-slate-900 border-b border-slate-100 pb-2">
          Add New Item
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {fields.map((field) => (
            <div key={field.key} className="space-y-1">
              {field.type === "textarea" ? (
                <textarea
                  placeholder={field.placeholder || field.label}
                  value={formData[field.key] || ""}
                  onChange={(e) => updateField(field.key, e.target.value)}
                  required={field.required}
                  className="w-full px-3 py-2 text-sm rounded border border-slate-300 h-20"
                />
              ) : (
                <input
                  type={field.type || "text"}
                  placeholder={field.placeholder || field.label}
                  value={formData[field.key] || ""}
                  onChange={(e) => updateField(field.key, e.target.value)}
                  required={field.required}
                  className="w-full px-3 py-2 text-sm rounded border border-slate-300"
                />
              )}
            </div>
          ))}
        </div>
        <button
          type="submit"
          className="px-6 py-2 bg-blue-600 text-white text-sm font-bold rounded-lg hover:bg-blue-700"
        >
          Create
        </button>
      </form>

      {status === "loading" ? (
        <Skeleton rows={4} />
      ) : status === "empty" ? (
        <div className="p-8 text-center bg-white rounded-2xl border border-slate-200 text-slate-500">
          No items added yet.
        </div>
      ) : (
        <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden">
          <table className="w-full">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                {columns.map((col) => (
                  <th
                    key={col.key}
                    className="px-4 py-3 text-left text-xs font-semibold text-slate-600 uppercase"
                  >
                    {col.label}
                  </th>
                ))}
                <th className="px-4 py-3 text-right text-xs font-semibold text-slate-600 uppercase">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {items.map((item) => (
                <tr key={item.id} className="hover:bg-slate-50">
                  {columns.map((col) => (
                    <td key={col.key} className="px-4 py-3 text-sm text-slate-700">
                      {col.render ? col.render(item) : item[col.key]}
                    </td>
                  ))}
                  <td className="px-4 py-3 text-right">
                    <button
                      onClick={() => handleDelete(item.id)}
                      className="px-3 py-1 bg-red-100 hover:bg-red-200 text-red-700 text-xs font-bold rounded"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
