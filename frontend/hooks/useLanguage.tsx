"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import { Lang } from "@/types";

interface LanguageContextType {
  lang: Lang;
  setLang: (lang: Lang) => void;
}

const LanguageContext = createContext<LanguageContextType>({
  lang: "en",
  setLang: () => {},
});

export const LanguageProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [lang, setLangState] = useState<Lang>("en");

  useEffect(() => {
    const stored = localStorage.getItem("app_lang") as Lang;
    if (stored === "en" || stored === "fa") {
      setLangState(stored);
    }
  }, []);

  const setLang = (newLang: Lang) => {
    setLangState(newLang);
    if (typeof window !== "undefined") {
      localStorage.setItem("app_lang", newLang);
    }
  };

  return (
    <LanguageContext.Provider value={{ lang, setLang }}>
      <div dir={lang === "fa" ? "rtl" : "ltr"} className={lang === "fa" ? "font-sans text-right" : "font-sans text-left"}>
        {children}
      </div>
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => useContext(LanguageContext);
