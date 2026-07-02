"use client";

import React from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";

export const AdminNavbar: React.FC = () => {
  const pathname = usePathname();
  const router = useRouter();

  if (pathname === "/adshs/login") {
    return null;
  }

  const handleLogout = async () => {
    // Call backend logout endpoint to clear HttpOnly cookie
    try {
      await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/admin/logout`, {
        method: "POST",
        credentials: "include",
      });
    } catch {
      // Ignore errors, proceed with local cleanup
    }
    // Clear UI state flag
    if (typeof window !== "undefined") {
      localStorage.removeItem("admin_logged_in");
    }
    router.push("/adshs/login");
  };

  const navLinks = [
    { href: "/adshs/dashboard", label: "Dashboard" },
    { href: "/adshs/profile", label: "Profile" },
    { href: "/adshs/skills", label: "Skills" },
    { href: "/adshs/projects", label: "Projects" },
    { href: "/adshs/experience", label: "Experience" },
    { href: "/adshs/education", label: "Education" },
    { href: "/adshs/courses", label: "Courses" },
    { href: "/adshs/certificates", label: "Certificates" },
    { href: "/adshs/social-links", label: "Social Links" },
    { href: "/adshs/ai-knowledge", label: "AI Knowledge" },
  ];

  return (
    <nav className="bg-slate-800 text-white shadow-lg">
      <div className="max-w-6xl mx-auto px-4 py-3 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-6">
          <Link href="/adshs/dashboard" className="text-lg font-bold text-amber-400">
            Admin Portal
          </Link>
          <div className="flex items-center gap-4 text-sm font-medium">
            {navLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className={`transition ${pathname === link.href ? "text-amber-400 font-bold underline" : "hover:text-slate-300"}`}
              >
                {link.label}
              </Link>
            ))}
          </div>
        </div>
        <div className="flex items-center gap-4">
          <Link href="/" className="text-xs text-slate-300 hover:text-white transition">
            View Public Site
          </Link>
          <button
            onClick={handleLogout}
            className="text-xs px-3 py-1 bg-red-600 hover:bg-red-500 rounded font-semibold transition"
          >
            Logout
          </button>
        </div>
      </div>
    </nav>
  );
};
