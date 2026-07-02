"use client";

import React, { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { AdminNavbar } from "@/components/AdminNavbar";

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    if (pathname === "/adshs/login") {
      setChecking(false);
      return;
    }

    const isLoggedIn = typeof window !== "undefined" ? localStorage.getItem("admin_logged_in") === "true" : false;
    if (!isLoggedIn) {
      router.push("/adshs/login");
    } else {
      setChecking(false);
    }
  }, [pathname, router]);

  if (checking && pathname !== "/adshs/login") {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-900 text-white">
        <div className="flex items-center gap-2">
          <span className="animate-spin">⏳</span>
          <span className="text-sm font-semibold">Checking authentication...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col min-h-screen bg-slate-50">
      <AdminNavbar />
      <main className="flex-grow">{children}</main>
    </div>
  );
}
