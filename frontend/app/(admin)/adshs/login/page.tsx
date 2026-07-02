"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { adminLoginService } from "@/services/admin.service";
import { normalizeError } from "@/lib/api";
import { UIStateStatus } from "@/types";

export default function AdminLoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [status, setStatus] = useState<UIStateStatus>("idle");
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) return;

    setStatus("loading");
    setErrorMsg(null);

    try {
      const res = await adminLoginService(email, password);
      if (res && res.isValid && res.data?.access_token) {
        // Cookie is set by backend (HttpOnly Secure SameSite=Strict)
        // Set a non-sensitive flag in localStorage for UI state only
        if (typeof window !== "undefined") {
          localStorage.setItem("admin_logged_in", "true");
        }
        setStatus("success");
        router.push("/adshs/dashboard");
      } else {
        setErrorMsg("Login failed: Missing access token in response.");
        setStatus("error");
      }
    } catch (err: unknown) {
      const normErr = normalizeError(err);
      setErrorMsg(normErr.message);
      setStatus("error");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-900 px-4 py-12">
      <div className="max-w-md w-full bg-slate-800 border border-slate-700 rounded-2xl p-8 shadow-2xl text-white space-y-6">
        <div className="text-center space-y-2">
          <h1 className="text-2xl font-extrabold text-amber-400">🔐 Admin Portal Login</h1>
          <p className="text-xs text-slate-400">Authenticate to manage content and RAG index.</p>
        </div>

        {status === "error" && errorMsg && (
          <div className="p-3 rounded bg-red-900/50 border border-red-500 text-red-200 text-xs text-center">
            {errorMsg}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">Email Address</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="admin@example.com"
              disabled={status === "loading"}
              className="w-full px-4 py-2.5 rounded-lg bg-slate-900 border border-slate-700 text-sm text-white focus:outline-none focus:border-amber-400 disabled:opacity-50"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">Password</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              disabled={status === "loading"}
              className="w-full px-4 py-2.5 rounded-lg bg-slate-900 border border-slate-700 text-sm text-white focus:outline-none focus:border-amber-400 disabled:opacity-50"
            />
          </div>

          <button
            type="submit"
            disabled={status === "loading"}
            className="w-full py-3 bg-amber-500 hover:bg-amber-600 disabled:opacity-50 text-slate-950 font-bold rounded-lg transition text-sm"
          >
            {status === "loading" ? "Authenticating..." : "Sign In"}
          </button>
        </form>
      </div>
    </div>
  );
}
