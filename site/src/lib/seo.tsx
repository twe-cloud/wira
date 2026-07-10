import { useEffect } from "react";
import { useLocation } from "react-router-dom";
import { FAQS, PRODUCT, PRICING } from "./brand";

type SeoProps = {
  title: string;
  description: string;
  path?: string;
  noindex?: boolean;
  structuredData?: Record<string, unknown> | Record<string, unknown>[];
};

function absoluteUrl(path = "/"): string {
  const normalized = path.startsWith("/") ? path : `/${path}`;
  return `${PRODUCT.siteUrl}${normalized}`;
}

function upsertMeta(selector: string, create: () => HTMLMetaElement, value: string) {
  const existing = document.head.querySelector(selector) as HTMLMetaElement | null;
  const el = existing || create();
  el.setAttribute("content", value);
  if (!existing) document.head.appendChild(el);
}

function upsertLink(rel: string, href: string) {
  const existing = document.head.querySelector(`link[rel="${rel}"]`) as HTMLLinkElement | null;
  const el = existing || document.createElement("link");
  el.setAttribute("rel", rel);
  el.setAttribute("href", href);
  if (!existing) document.head.appendChild(el);
}

function setJsonLd(data?: SeoProps["structuredData"]) {
  document.querySelectorAll('script[data-wira-seo="route"]').forEach((node) => node.remove());
  if (!data) return;
  const script = document.createElement("script");
  script.type = "application/ld+json";
  script.dataset.wiraSeo = "route";
  script.textContent = JSON.stringify(data);
  document.head.appendChild(script);
}

export function Seo({ title, description, path, noindex, structuredData }: SeoProps) {
  const location = useLocation();
  const routePath = path || location.pathname || "/";
  const canonical = absoluteUrl(routePath);
  const fullTitle = title.includes(PRODUCT.name) ? title : `${title} | ${PRODUCT.name}`;

  useEffect(() => {
    document.title = fullTitle;
    upsertMeta('meta[name="description"]', () => {
      const meta = document.createElement("meta");
      meta.setAttribute("name", "description");
      return meta;
    }, description);
    upsertMeta('meta[name="robots"]', () => {
      const meta = document.createElement("meta");
      meta.setAttribute("name", "robots");
      return meta;
    }, noindex ? "noindex,follow" : "index,follow");
    upsertMeta('meta[property="og:title"]', () => {
      const meta = document.createElement("meta");
      meta.setAttribute("property", "og:title");
      return meta;
    }, fullTitle);
    upsertMeta('meta[property="og:description"]', () => {
      const meta = document.createElement("meta");
      meta.setAttribute("property", "og:description");
      return meta;
    }, description);
    upsertMeta('meta[property="og:url"]', () => {
      const meta = document.createElement("meta");
      meta.setAttribute("property", "og:url");
      return meta;
    }, canonical);
    upsertMeta('meta[name="twitter:title"]', () => {
      const meta = document.createElement("meta");
      meta.setAttribute("name", "twitter:title");
      return meta;
    }, fullTitle);
    upsertMeta('meta[name="twitter:description"]', () => {
      const meta = document.createElement("meta");
      meta.setAttribute("name", "twitter:description");
      return meta;
    }, description);
    upsertLink("canonical", canonical);
    setJsonLd(structuredData);
  }, [canonical, description, fullTitle, noindex, structuredData]);

  return null;
}

export function softwareApplicationSchema() {
  return {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    name: PRODUCT.name,
    applicationCategory: "BusinessApplication",
    operatingSystem: "macOS",
    url: PRODUCT.siteUrl,
    image: `${PRODUCT.siteUrl}/wira-logo.png`,
    description: PRODUCT.description,
    offers: {
      "@type": "Offer",
      price: String(PRICING.local.price),
      priceCurrency: "USD",
      availability: "https://schema.org/InStock",
      url: `${PRODUCT.siteUrl}/#pricing`,
    },
    brand: { "@type": "Brand", name: PRODUCT.name },
    publisher: {
      "@type": "Organization",
      name: PRODUCT.legalEntity,
      url: "https://nibiashara.biz/",
    },
  };
}

export function faqSchema() {
  return {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: FAQS.map((faq) => ({
      "@type": "Question",
      name: faq.q,
      acceptedAnswer: {
        "@type": "Answer",
        text: faq.a,
      },
    })),
  };
}

export function websiteSchema() {
  return {
    "@context": "https://schema.org",
    "@type": "WebSite",
    name: PRODUCT.name,
    url: PRODUCT.siteUrl,
    description: PRODUCT.description,
    publisher: {
      "@type": "Organization",
      name: PRODUCT.legalEntity,
      url: "https://nibiashara.biz/",
    },
  };
}

