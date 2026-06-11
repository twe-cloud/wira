import { describe, it, expect, vi, afterEach } from "vitest";
import worker from "./worker";
import {
  WIRA_LOCAL_PRICE,
  DOWNLOADS,
  allowedOrigin,
  corsHeaders,
  sanitizeSiteBase,
  uniqueUrls,
  defaultDownloadUrl,
  pinnedDownloadUrl,
  downloadSourceUrls,
  resolveLatestGithubDownloadUrl,
  GITHUB_LATEST_RELEASE_TIMEOUT_MS,
} from "./worker-lib";

const SITE = "https://wira-local-agent.nibiashara.workers.dev";

// Minimal Env stub. ASSETS.fetch returns a sentinel so we can assert fall-through.
function makeEnv(overrides: Record<string, unknown> = {}) {
  return {
    ASSETS: { fetch: vi.fn(async () => new Response("asset", { status: 200 })) },
    SITE_URL: SITE,
    ...overrides,
  } as never;
}

const req = (path: string, init?: RequestInit) => new Request(`${SITE}${path}`, init);

afterEach(() => {
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
  vi.useRealTimers(); // restoreAllMocks doesn't reset fake timers; prevent leak on test failure
});

describe("allowedOrigin / CORS allowlist", () => {
  const env = makeEnv();
  it("allows the canonical nibiashara.biz origin", () => {
    expect(allowedOrigin("https://nibiashara.biz", env)).toBe("https://nibiashara.biz");
  });
  it("allows the configured SITE_URL origin", () => {
    expect(allowedOrigin(SITE, env)).toBe(SITE);
  });
  it("rejects an unknown origin", () => {
    expect(allowedOrigin("https://evil.example", env)).toBeNull();
  });
  it("rejects a null origin", () => {
    expect(allowedOrigin(null, env)).toBeNull();
  });
  it("corsHeaders reflects only allowed origins, {} otherwise", () => {
    expect(corsHeaders("https://nibiashara.biz", env)).toMatchObject({
      "Access-Control-Allow-Origin": "https://nibiashara.biz",
    });
    expect(corsHeaders("https://evil.example", env)).toEqual({});
  });
});

describe("sanitizeSiteBase (open-redirect guard)", () => {
  const env = makeEnv();
  const request = req("/api/checkout", { headers: { origin: "https://nibiashara.biz" } });
  it("maps the embedded nibiashara.biz/wira path", () => {
    expect(sanitizeSiteBase("https://nibiashara.biz/wira/", request, env)).toBe(
      "https://nibiashara.biz/wira",
    );
  });
  it("normalizes a SITE_URL-origin base (strips trailing slash)", () => {
    expect(sanitizeSiteBase(`${SITE}/`, request, env)).toBe(SITE);
  });
  it("refuses an attacker origin and falls back to SITE_URL", () => {
    expect(sanitizeSiteBase("https://evil.example/phish", request, env)).toBe(SITE);
  });
  it("falls back when siteBase is missing", () => {
    expect(sanitizeSiteBase(undefined, request, env)).toBe(SITE);
  });
  it("falls back on a malformed siteBase", () => {
    expect(sanitizeSiteBase("not a url", request, env)).toBe(SITE);
  });
  it("never trusts the request Origin header as the fallback base", () => {
    const noSiteEnv = makeEnv({ SITE_URL: undefined });
    const hostileOriginRequest = req("/api/checkout", {
      headers: { origin: "https://evil.example" },
    });
    expect(sanitizeSiteBase(undefined, hostileOriginRequest, noSiteEnv)).toBe(SITE);
  });
});

describe("download URL helpers", () => {
  it("uniqueUrls trims, de-dupes, drops falsy", () => {
    expect(uniqueUrls([" a ", "a", undefined, "", null, "b"])).toEqual(["a", "b"]);
  });
  it("builds latest + pinned URLs per platform", () => {
    expect(defaultDownloadUrl(DOWNLOADS.mac)).toContain("/latest/download/Wira.dmg");
    expect(pinnedDownloadUrl(DOWNLOADS.windows)).toContain(
      `/download/${DOWNLOADS.windows.pinnedTag}/WiraSetup.exe`,
    );
  });
  it("downloadSourceUrls: env override first, dedup, drops a failed GitHub lookup", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => {
        throw new Error("no network in tests");
      }),
    );
    const env = makeEnv({ WIRA_DOWNLOAD_URL: "https://cdn.example/Wira.dmg" });
    const urls = await downloadSourceUrls(env, DOWNLOADS.mac);
    expect(urls[0]).toBe("https://cdn.example/Wira.dmg");
    expect(urls).toContain(defaultDownloadUrl(DOWNLOADS.mac));
    expect(urls).toContain(pinnedDownloadUrl(DOWNLOADS.mac));
    expect(new Set(urls).size).toBe(urls.length); // no duplicates
  });
  it("resolveLatestGithubDownloadUrl aborts slow GitHub lookups", async () => {
    vi.useFakeTimers();
    vi.stubGlobal(
      "fetch",
      vi.fn((_, init?: RequestInit) => {
        const signal = init?.signal as AbortSignal | undefined;
        return new Promise((_, reject) => {
          signal?.addEventListener("abort", () => {
            reject(new DOMException("The operation was aborted.", "AbortError"));
          });
        });
      }),
    );

    const lookup = resolveLatestGithubDownloadUrl("Wira.dmg");
    await vi.advanceTimersByTimeAsync(GITHUB_LATEST_RELEASE_TIMEOUT_MS);
    await expect(lookup).resolves.toBeNull();
    vi.useRealTimers();
  });
});

describe("fetch handler guards", () => {
  const jsonHeaders = { "content-type": "application/json", origin: "https://nibiashara.biz" };

  it("OPTIONS /api/checkout → 204 with CORS for an allowed origin", async () => {
    const res = await worker.fetch(
      req("/api/checkout", { method: "OPTIONS", headers: { origin: "https://nibiashara.biz" } }),
      makeEnv(),
    );
    expect(res.status).toBe(204);
    expect(res.headers.get("Access-Control-Allow-Origin")).toBe("https://nibiashara.biz");
  });

  it("rejects checkout with an unknown priceId → 400", async () => {
    const res = await worker.fetch(
      req("/api/checkout", { method: "POST", headers: jsonHeaders, body: JSON.stringify({ priceId: "price_evil" }) }),
      makeEnv({ STRIPE_SECRET_KEY: "sk_test_x" }),
    );
    expect(res.status).toBe(400);
  });

  it("returns 500 when STRIPE_SECRET_KEY is missing", async () => {
    const res = await worker.fetch(
      req("/api/checkout", { method: "POST", headers: jsonHeaders, body: JSON.stringify({ priceId: WIRA_LOCAL_PRICE }) }),
      makeEnv({ STRIPE_SECRET_KEY: undefined }),
    );
    expect(res.status).toBe(500);
  });

  it("webhook without a stripe-signature header → 400", async () => {
    const res = await worker.fetch(
      req("/api/webhook", { method: "POST", body: "{}" }),
      makeEnv({ STRIPE_SECRET_KEY: "sk_test_x", STRIPE_WHSEC: "whsec_x" }),
    );
    expect(res.status).toBe(400);
  });

  it("webhook is 500 when signing secrets are unset", async () => {
    const res = await worker.fetch(
      req("/api/webhook", { method: "POST", headers: { "stripe-signature": "t=1,v1=x" }, body: "{}" }),
      makeEnv({ STRIPE_SECRET_KEY: undefined, STRIPE_WHSEC: undefined }),
    );
    expect(res.status).toBe(500);
  });

  it("webhook with a non-POST method → 405", async () => {
    const res = await worker.fetch(
      req("/api/webhook", { method: "GET" }),
      makeEnv({ STRIPE_SECRET_KEY: "sk_test_x", STRIPE_WHSEC: "whsec_x" }),
    );
    expect(res.status).toBe(405);
  });

  it("download route rejects non-GET/HEAD → 405", async () => {
    const res = await worker.fetch(req("/download/wira-mac", { method: "POST" }), makeEnv());
    expect(res.status).toBe(405);
  });

  it("unknown path falls through to ASSETS", async () => {
    const env = makeEnv();
    const res = await worker.fetch(req("/anything"), env);
    expect((env as { ASSETS: { fetch: ReturnType<typeof vi.fn> } }).ASSETS.fetch).toHaveBeenCalled();
    expect(res.status).toBe(200);
  });
});
