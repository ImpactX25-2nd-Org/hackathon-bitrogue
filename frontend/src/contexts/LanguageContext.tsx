import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { useTranslation as useI18n } from "../lib/translations";

export const languages = [
  { code: "en", name: "English", nativeName: "English" },
  { code: "ta", name: "Tamil", nativeName: "தமிழ்" },
  { code: "kn", name: "Kannada", nativeName: "ಕನ್ನಡ" },
];

interface LanguageContextType {
  currentLanguage: string;
  setLanguage: (code: string) => void;
  getLanguageName: (code: string) => string;
  t: (key: string) => string; // Translation function
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export const LanguageProvider = ({ children }: { children: ReactNode }) => {
  const [currentLanguage, setCurrentLanguage] = useState<string>(() => {
    // Initialize from localStorage or default to English
    return localStorage.getItem("preferredLanguage") || "en";
  });

  // Translation function
  const { t } = useI18n(currentLanguage);

  const setLanguage = (code: string) => {
    setCurrentLanguage(code);
    localStorage.setItem("preferredLanguage", code);
    
    // Dispatch custom event so other components can react
    window.dispatchEvent(new CustomEvent("languageChange", { detail: code }));
  };

  const getLanguageName = (code: string) => {
    return languages.find(lang => lang.code === code)?.nativeName || "English";
  };

  useEffect(() => {
    // Sync with localStorage changes from other tabs/windows
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === "preferredLanguage" && e.newValue) {
        setCurrentLanguage(e.newValue);
      }
    };

    window.addEventListener("storage", handleStorageChange);
    return () => window.removeEventListener("storage", handleStorageChange);
  }, []);

  return (
    <LanguageContext.Provider value={{ currentLanguage, setLanguage, getLanguageName, t }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (context === undefined) {
    throw new Error("useLanguage must be used within a LanguageProvider");
  }
  return context;
};
