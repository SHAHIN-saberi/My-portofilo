import { MetadataRoute } from "next";

const BASE_URL = process.env.NEXT_PUBLIC_SITE_URL || "https://shahinsaberi.com";

export default function sitemap(): MetadataRoute.Sitemap {
  const routes = [
    "",
    "/projects",
    "/skills",
    "/experience",
    "/education",
    "/chat",
  ];

  const sitemapEntries: MetadataRoute.Sitemap = routes.map((route) => ({
    url: `${BASE_URL}${route}`,
    lastModified: new Date(),
    changeFrequency: route === "" ? "weekly" : "monthly",
    priority: route === "" ? 1.0 : 0.8,
  }));

  // Add language variants
  const langRoutes = ["/en", "/fa"];
  langRoutes.forEach((lang) => {
    routes.forEach((route) => {
      sitemapEntries.push({
        url: `${BASE_URL}${lang}${route}`,
        lastModified: new Date(),
        changeFrequency: route === "" ? "weekly" : "monthly",
        priority: route === "" ? 0.9 : 0.7,
      });
    });
  });

  return sitemapEntries;
}
