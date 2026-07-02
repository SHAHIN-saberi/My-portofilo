"use client";

import React, { useEffect, useState } from "react";
import { getProfileService, getSocialLinksService } from "@/services/public.service";
import { normalizeError } from "@/lib/api";
import { Profile, SocialLink, UIState } from "@/types";
import { IDENTITY_FALLBACK } from "@/lib/identity";

export const Footer: React.FC = () => {
  const [links, setLinks] = useState<SocialLink[]>([]);
  const [profile, setProfile] = useState<Profile | null>(null);
  const [status, setStatus] = useState<UIState>("loading");
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    setStatus("loading");
    Promise.all([
      getSocialLinksService().catch(() => ({ data: [], isValid: false })),
      getProfileService("en").catch(() => ({ data: null, isValid: false })),
    ])
      .then(([linksRes, profRes]) => {
        if (mounted) {
          setLinks((linksRes.data || []).filter((l) => l.is_visible !== false));
          if (profRes.isValid && profRes.data) {
            setProfile(profRes.data);
          }
          setStatus("success");
        }
      })
      .catch((err) => {
        if (mounted) {
          const normErr = normalizeError(err);
          setErrorMsg(normErr.message);
          setStatus("error");
        }
      });
    return () => {
      mounted = false;
    };
  }, []);

  // Field-Level Fallback ONLY
  const phone = profile?.phone ?? IDENTITY_FALLBACK.contact.phone;
  const email = profile?.email ?? IDENTITY_FALLBACK.contact.email;
  const location = profile?.location ?? IDENTITY_FALLBACK.location;
  const name = profile?.name ?? IDENTITY_FALLBACK.fullName;

  const displayLinks: { platform: string; url: string }[] =
    links.length > 0
      ? links.map((l) => ({ platform: l.platform || "Link", url: l.url || "#" }))
      : [
          { platform: "GitHub", url: IDENTITY_FALLBACK.links.github },
          { platform: "LinkedIn", url: IDENTITY_FALLBACK.links.linkedin },
          { platform: "Telegram", url: IDENTITY_FALLBACK.links.telegram },
        ];

  return (
    <footer className="bg-slate-900 text-slate-400 py-8 border-t border-slate-800 mt-16">
      <div className="max-w-6xl mx-auto px-4 flex flex-col items-center justify-center gap-6">
        <div className="flex flex-wrap items-center justify-center gap-6 text-xs text-slate-300 font-medium">
          {phone && <span>📞 {phone}</span>}
          {email && (
            <a href={`mailto:${email}`} className="hover:text-blue-400 transition">
              ✉️ {email}
            </a>
          )}
          {location && <span>📍 {location}</span>}
        </div>

        <div className="flex flex-wrap items-center justify-center gap-6">
          {displayLinks.map(({ platform, url }, idx) => (
            <a
              key={idx}
              href={url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm font-semibold text-slate-300 hover:text-blue-400 transition underline decoration-slate-700 hover:decoration-blue-400"
            >
              {platform}
            </a>
          ))}
        </div>

        {status === "error" && errorMsg && (
          <span className="text-[10px] text-amber-500">Note: Displaying emergency fallback info ({errorMsg})</span>
        )}

        <div className="flex flex-wrap items-center justify-center gap-6 text-xs text-slate-500">
          <a href="/privacy" className="hover:text-blue-400 transition">
            Privacy Notice
          </a>
          <span>•</span>
          <span>© {new Date().getFullYear()} {name}. All rights reserved.</span>
        </div>
      </div>
    </footer>
  );
};
