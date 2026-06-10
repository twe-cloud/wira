/**
 * Pure helpers + types for the Wira site Worker.
 *
 * These live in a NON-entry module on purpose: the Workers runtime treats every
 * named export of the entry module (worker.ts) as a handler and rejects values
 * that aren't functions/handlers (e.g. a string constant). Keeping the testable
 * helpers here lets worker.test.ts import them while worker.ts exposes only
 * `export default { fetch }`.
 */

export const WIRA_LOCAL_PRICE = "price_1TcrAXRVrXHv0YFpfmw35hIw";
export const RELEASE_DOWNLOAD_BASE = "https://github.com/twe-cloud/wira/releases";
export const GITHUB_LATEST_RELEASE_API =
  "https://api.github.com/repos/twe-cloud/wira/releases/latest";
export const DOWNLOAD_CACHE_TTL_SECONDS = 60 * 60 * 24;

export const CHECKOUT_PRODUCT_NAME = "Wira";
export const CHECKOUT_PRODUCT_DESCRIPTION =
  "Your own AI agent on WhatsApp. Start free, connect ChatGPT, or keep the brain private when your machine is a good fit.";

export type PlatformKey = "mac" | "windows";

export interface DownloadSpec {
  key: PlatformKey;
  path: string;
  filename: string;
  contentType: string;
  // Last-resort pinned tag if "latest" can't be resolved.
  pinnedTag: string;
}

// Both artifacts are produced by the same release pipeline (see
// .github/workflows/build-windows.yml + agent/scripts/build-app.sh). Mac is GA;
// the Windows .exe ships today as an unsigned early beta.
export const DOWNLOADS: Record<PlatformKey, DownloadSpec> = {
  mac: {
    key: "mac",
    path: "/download/wira-mac",
    filename: "Wira.dmg",
    contentType: "application/x-apple-diskimage",
    pinnedTag: "v1.0.7",
  },
  windows: {
    key: "windows",
    path: "/download/wira-windows",
    filename: "WiraSetup.exe",
    contentType: "application/vnd.microsoft.portable-executable",
    pinnedTag: "v1.0.7",
  },
};

export interface Env {
  ASSETS: Fetcher;
  STRIPE_SECRET_KEY?: string;
  STRIPE_WHSEC?: string;
  SITE_URL?: string;
  WIRA_DOWNLOAD_URL?: string;
  WIRA_DOWNLOAD_FALLBACK_URL?: string;
  WIRA_WINDOWS_DOWNLOAD_URL?: string;
  // Optional — best-effort transactional download email. If unset, the buyer
  // still gets the download from the /success page + the Stripe receipt.
  RESEND_API_KEY?: string;
  RESEND_FROM?: string;
}

export function json(status: number, body: unknown, headers?: HeadersInit): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      "Content-Type": "application/json",
      ...(headers || {}),
    },
  });
}

// Only reflect Origin for known site origins, never an arbitrary caller.
export function allowedOrigin(origin: string | null, env: Env): string | null {
  if (!origin) return null;
  const allowed = new Set<string>(["https://nibiashara.biz"]);
  if (env.SITE_URL) {
    try {
      allowed.add(new URL(env.SITE_URL).origin);
    } catch {
      // ignore a malformed SITE_URL
    }
  }
  return allowed.has(origin) ? origin : null;
}

export function corsHeaders(origin: string | null, env: Env): HeadersInit {
  const o = allowedOrigin(origin, env);
  if (!o) return {};
  return {
    "Access-Control-Allow-Origin": o,
    Vary: "Origin",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
  };
}

export function sanitizeSiteBase(siteBase: string | undefined, request: Request, env: Env): string {
  const fallback = env.SITE_URL || request.headers.get("origin") || "";
  if (!siteBase) return fallback;
  try {
    const url = new URL(siteBase);
    if (
      url.origin === "https://nibiashara.biz" &&
      (url.pathname === "/wira" || url.pathname === "/wira/")
    ) {
      return "https://nibiashara.biz/wira";
    }
    if (env.SITE_URL && url.origin === new URL(env.SITE_URL).origin) {
      return `${url.origin}${url.pathname.replace(/\/$/, "")}`;
    }
  } catch {
    return fallback;
  }
  return fallback;
}

export function uniqueUrls(urls: Array<string | undefined | null>): string[] {
  return [...new Set(urls.map((url) => url?.trim()).filter(Boolean) as string[])];
}

export function defaultDownloadUrl(spec: DownloadSpec): string {
  return `${RELEASE_DOWNLOAD_BASE}/latest/download/${spec.filename}`;
}

export function pinnedDownloadUrl(spec: DownloadSpec): string {
  return `${RELEASE_DOWNLOAD_BASE}/download/${spec.pinnedTag}/${spec.filename}`;
}

export function envDownloadOverride(env: Env, spec: DownloadSpec): string | undefined {
  return spec.key === "mac" ? env.WIRA_DOWNLOAD_URL : env.WIRA_WINDOWS_DOWNLOAD_URL;
}

export function publicDownloadUrl(env: Env, spec: DownloadSpec, siteUrl?: string): string {
  if (siteUrl) {
    return `${siteUrl}${spec.path}`;
  }
  return envDownloadOverride(env, spec) || defaultDownloadUrl(spec);
}

export async function resolveLatestGithubDownloadUrl(filename: string): Promise<string | null> {
  try {
    const response = await fetch(GITHUB_LATEST_RELEASE_API, {
      headers: {
        Accept: "application/vnd.github+json",
        "User-Agent": "WiraDownloadResolver/1.0",
      },
    });
    if (!response.ok) {
      console.warn("Latest release lookup failed:", response.status);
      return null;
    }

    const data = (await response.json()) as {
      assets?: Array<{ name?: string; browser_download_url?: string }>;
    };
    const asset = data.assets?.find((a) => a.name === filename)?.browser_download_url;
    return asset || null;
  } catch (error) {
    console.warn(
      "Latest release lookup errored:",
      error instanceof Error ? error.message : String(error),
    );
    return null;
  }
}

export async function downloadSourceUrls(env: Env, spec: DownloadSpec): Promise<string[]> {
  const latestGithubAsset = await resolveLatestGithubDownloadUrl(spec.filename);
  return uniqueUrls([
    envDownloadOverride(env, spec),
    defaultDownloadUrl(spec),
    latestGithubAsset,
    spec.key === "mac" ? env.WIRA_DOWNLOAD_FALLBACK_URL : undefined,
    pinnedDownloadUrl(spec),
  ]);
}

export function finalizeDownloadResponse(upstream: Response, spec: DownloadSpec): Response {
  const headers = new Headers(upstream.headers);
  headers.set(
    "Cache-Control",
    `public, max-age=0, s-maxage=${DOWNLOAD_CACHE_TTL_SECONDS}, stale-while-revalidate=86400`,
  );
  headers.set("Content-Disposition", `attachment; filename="${spec.filename}"`);
  headers.set("Content-Type", headers.get("Content-Type") || spec.contentType);
  headers.set("X-Content-Type-Options", "nosniff");
  return new Response(upstream.body, {
    status: upstream.status,
    headers,
  });
}
