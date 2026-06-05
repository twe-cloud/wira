/**
 * Wira site Worker (Cloudflare).
 *
 * Serves the built Vite SPA from the ASSETS binding and handles the two
 * Stripe API routes that used to live in Netlify Functions:
 *   POST /api/checkout  — create a Stripe Checkout Session
 *   POST /api/webhook   — receive + verify Stripe webhook events
 *
 * Static assets are served directly by the assets runtime; this Worker only
 * runs first for `/api/*` (see wrangler.jsonc `run_worker_first`).
 */
import Stripe from "stripe";

const WIRA_LOCAL_PRICE = "price_1TcrAXRVrXHv0YFpfmw35hIw";
const DOWNLOAD_PATH = "/download/wira-mac";
const DEFAULT_DOWNLOAD_URL =
  "https://github.com/twe-cloud/wira/releases/latest/download/Wira.dmg";
const PINNED_DOWNLOAD_URL =
  "https://github.com/twe-cloud/wira/releases/download/v1.0.7/Wira.dmg";
const GITHUB_LATEST_RELEASE_API =
  "https://api.github.com/repos/twe-cloud/wira/releases/latest";
const DOWNLOAD_FILENAME = "Wira.dmg";
const DOWNLOAD_CACHE_TTL_SECONDS = 60 * 60 * 24;
const CHECKOUT_PRODUCT_NAME = "Wira";
const CHECKOUT_PRODUCT_DESCRIPTION =
  "Your own AI agent on WhatsApp. Start free, connect ChatGPT, or keep it private on your Mac.";

interface Env {
  ASSETS: Fetcher;
  STRIPE_SECRET_KEY?: string;
  STRIPE_WHSEC?: string;
  SITE_URL?: string;
  WIRA_DOWNLOAD_URL?: string;
  WIRA_DOWNLOAD_FALLBACK_URL?: string;
  // Optional — best-effort transactional download email. If unset, the buyer
  // still gets the download from the /success page + the Stripe receipt.
  RESEND_API_KEY?: string;
  RESEND_FROM?: string;
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);

    if (url.pathname === "/api/checkout") {
      if (request.method === "OPTIONS") {
        return new Response(null, { status: 204, headers: corsHeaders(request.headers.get("origin")) });
      }
      return handleCheckout(request, env);
    }
    if (url.pathname === "/api/webhook") {
      return handleWebhook(request, env);
    }
    if (url.pathname === DOWNLOAD_PATH) {
      return handleDownload(request, env);
    }

    // Everything else: the SPA / static assets.
    return env.ASSETS.fetch(request);
  },
} satisfies ExportedHandler<Env>;

function stripeClient(secret: string): Stripe {
  // Workers has no Node TCP stack; use the fetch-based HTTP client.
  return new Stripe(secret, {
    httpClient: Stripe.createFetchHttpClient(),
  });
}

function json(status: number, body: unknown, headers?: HeadersInit): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      "Content-Type": "application/json",
      ...(headers || {}),
    },
  });
}

function corsHeaders(origin: string | null): HeadersInit {
  if (!origin) return {};
  return {
    "Access-Control-Allow-Origin": origin,
    Vary: "Origin",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
  };
}

function sanitizeSiteBase(siteBase: string | undefined, request: Request, env: Env): string {
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

function uniqueUrls(urls: Array<string | undefined | null>): string[] {
  return [...new Set(urls.map((url) => url?.trim()).filter(Boolean) as string[])];
}

function publicDownloadUrl(env: Env, siteUrl?: string): string {
  if (siteUrl) {
    return `${siteUrl}${DOWNLOAD_PATH}`;
  }
  return env.WIRA_DOWNLOAD_URL || DEFAULT_DOWNLOAD_URL;
}

async function resolveLatestGithubDownloadUrl(): Promise<string | null> {
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
    const dmg = data.assets?.find((asset) => asset.name === DOWNLOAD_FILENAME)?.browser_download_url;
    return dmg || null;
  } catch (error) {
    console.warn(
      "Latest release lookup errored:",
      error instanceof Error ? error.message : String(error),
    );
    return null;
  }
}

async function downloadSourceUrls(env: Env): Promise<string[]> {
  const latestGithubAsset = await resolveLatestGithubDownloadUrl();
  return uniqueUrls([
    env.WIRA_DOWNLOAD_URL,
    DEFAULT_DOWNLOAD_URL,
    latestGithubAsset,
    env.WIRA_DOWNLOAD_FALLBACK_URL,
    PINNED_DOWNLOAD_URL,
  ]);
}

function finalizeDownloadResponse(upstream: Response, sourceUrl: string): Response {
  const headers = new Headers(upstream.headers);
  headers.set(
    "Cache-Control",
    `public, max-age=0, s-maxage=${DOWNLOAD_CACHE_TTL_SECONDS}, stale-while-revalidate=86400`,
  );
  headers.set("Content-Disposition", `attachment; filename="${DOWNLOAD_FILENAME}"`);
  headers.set(
    "Content-Type",
    headers.get("Content-Type") || "application/x-apple-diskimage",
  );
  headers.set("X-Content-Type-Options", "nosniff");
  headers.set("X-Wira-Download-Source", sourceUrl);
  return new Response(upstream.body, {
    status: upstream.status,
    headers,
  });
}

async function handleDownload(request: Request, env: Env): Promise<Response> {
  if (request.method !== "GET" && request.method !== "HEAD") {
    return new Response("Method not allowed", {
      status: 405,
      headers: { Allow: "GET, HEAD" },
    });
  }

  const cache = caches.default;
  const cacheKey = new Request(new URL(DOWNLOAD_PATH, request.url).toString(), {
    method: "GET",
  });
  const cached = await cache.match(cacheKey);
  if (cached) {
    if (request.method === "HEAD") {
      return new Response(null, { status: cached.status, headers: cached.headers });
    }
    return cached;
  }

  const sources = await downloadSourceUrls(env);
  let lastFailure = "no sources configured";

  for (const sourceUrl of sources) {
    try {
      const upstream = await fetch(sourceUrl, {
        method: "GET",
        redirect: "follow",
        cf: {
          cacheEverything: true,
          cacheTtl: DOWNLOAD_CACHE_TTL_SECONDS,
        },
      });
      if (!upstream.ok) {
        lastFailure = `${sourceUrl} -> ${upstream.status}`;
        continue;
      }

      const response = finalizeDownloadResponse(upstream, sourceUrl);
      await cache.put(cacheKey, response.clone());

      if (request.method === "HEAD") {
        return new Response(null, {
          status: response.status,
          headers: response.headers,
        });
      }
      return response;
    } catch (error) {
      lastFailure = `${sourceUrl} -> ${error instanceof Error ? error.message : String(error)}`;
    }
  }

  console.error("All Wira download sources failed:", lastFailure);
  return new Response(
    "Download temporarily unavailable. Please try again in a minute or email hello@wira.io.",
    {
      status: 503,
      headers: {
        "Content-Type": "text/plain; charset=utf-8",
        "Cache-Control": "no-store",
      },
    },
  );
}

async function handleCheckout(request: Request, env: Env): Promise<Response> {
  const origin = request.headers.get("origin");
  const cors = corsHeaders(origin);

  if (request.method !== "POST") {
    return json(405, { error: "Method not allowed" }, cors);
  }

  const secret = env.STRIPE_SECRET_KEY;
  if (!secret) {
    return json(500, { error: "Server is not configured (missing STRIPE_SECRET_KEY)." }, cors);
  }

  let priceId: string | undefined;
  let siteBase: string | undefined;
  try {
    ({ priceId, siteBase } = (await request.json()) as {
      priceId?: string;
      siteBase?: string;
    });
  } catch {
    return json(400, { error: "Invalid JSON body." }, cors);
  }
  if (priceId !== WIRA_LOCAL_PRICE) {
    return json(400, { error: "Missing or invalid priceId." }, cors);
  }

  const checkoutBase = sanitizeSiteBase(siteBase, request, env);
  if (!checkoutBase) {
    return json(500, { error: "Server is not configured (missing SITE_URL)." }, cors);
  }

  const stripe = stripeClient(secret);
  try {
    try {
      await syncCheckoutProductCopy(stripe, priceId);
    } catch (e) {
      console.warn("Stripe product copy sync failed:", e instanceof Error ? e.message : e);
    }

    const session = await stripe.checkout.sessions.create({
      mode: "payment",
      line_items: [{ price: priceId, quantity: 1 }],
      success_url: `${checkoutBase}/success?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${checkoutBase}/#pricing`,
      allow_promotion_codes: true,
      custom_text: {
        submit: {
          message:
            "After payment: download Wira, choose the fastest brain for you, then scan the WhatsApp QR.",
        },
      },
      billing_address_collection: "auto",
      automatic_tax: { enabled: false },
      metadata: { wira_tier: "local", billing_model: "one_time" },
    });
    return json(200, { url: session.url }, cors);
  } catch (e) {
    console.error("Stripe checkout error:", e instanceof Error ? e.message : e);
    return json(500, { error: "Could not create checkout session. Please try again." }, cors);
  }
}

async function syncCheckoutProductCopy(stripe: Stripe, priceId: string): Promise<void> {
  const price = await stripe.prices.retrieve(priceId, { expand: ["product"] });
  const product =
    typeof price.product === "string"
      ? await stripe.products.retrieve(price.product)
      : price.product;

  if (!product || product.deleted) {
    return;
  }

  if (
    product.name === CHECKOUT_PRODUCT_NAME &&
    product.description === CHECKOUT_PRODUCT_DESCRIPTION
  ) {
    return;
  }

  await stripe.products.update(product.id, {
    name: CHECKOUT_PRODUCT_NAME,
    description: CHECKOUT_PRODUCT_DESCRIPTION,
  });
}

async function sendDownloadEmail(
  env: Env,
  to: string,
  name?: string | null,
): Promise<void> {
  const apiKey = env.RESEND_API_KEY;
  const from = env.RESEND_FROM;
  if (!apiKey || !from) {
    console.log("Skipping download email (RESEND not configured).");
    return;
  }

  const siteUrl = env.SITE_URL || "";
  const downloadUrl = publicDownloadUrl(env, siteUrl);
  const greeting = name ? `Hi ${name},` : "Hi there,";
  const html = `
    <div style="font-family:-apple-system,Segoe UI,Roboto,sans-serif;max-width:520px;margin:0 auto;color:#1a2233">
      <h1 style="font-size:22px;margin:0 0 12px">You're in. Welcome to Wira.</h1>
      <p style="margin:0 0 16px;color:#5f6472">${greeting} thanks for your purchase. Wira is your own AI agent that runs on your Mac and answers you on WhatsApp.</p>
      <p style="margin:0 0 20px">
        <a href="${downloadUrl}" style="display:inline-block;background:#6f5318;color:#fff;text-decoration:none;padding:12px 20px;border-radius:10px;font-weight:600">Download Wira for Mac</a>
      </p>
      <p style="margin:0 0 8px;color:#5f6472;font-size:13px">Requires an Apple Silicon Mac (M1 or newer), macOS 12+.</p>
      <p style="margin:0 0 8px;color:#5f6472;font-size:13px">After installing: open Wira, choose how it should think, then scan the WhatsApp QR code. Start free, use ChatGPT, or keep it private on your Mac. Three steps and your agent is live.</p>
      ${siteUrl ? `<p style="margin:16px 0 0;color:#8d7550;font-size:12px">Need a hand? Just reply to this email, or follow the <a href="${siteUrl}/onboarding">guided setup walkthrough</a>.</p>` : ""}
    </div>`;

  const resp = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${apiKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      from,
      to,
      subject: "Your Wira download — install on your Mac",
      html,
    }),
  });
  if (!resp.ok) {
    throw new Error(`Resend ${resp.status}: ${await resp.text()}`);
  }
  console.log("Download email sent to", to);
}

async function handleWebhook(request: Request, env: Env): Promise<Response> {
  if (request.method !== "POST") {
    return new Response("Method not allowed", { status: 405 });
  }

  const secret = env.STRIPE_SECRET_KEY;
  const whsec = env.STRIPE_WHSEC;
  if (!secret || !whsec) {
    console.error("Missing STRIPE_SECRET_KEY or STRIPE_WHSEC");
    return new Response("Server not configured", { status: 500 });
  }

  const sig = request.headers.get("stripe-signature");
  if (!sig) {
    return new Response("Missing stripe-signature header", { status: 400 });
  }

  const stripe = stripeClient(secret);
  const raw = await request.text();

  let event: Stripe.Event;
  try {
    // Workers crypto is async-only — must use constructEventAsync + SubtleCrypto.
    event = await stripe.webhooks.constructEventAsync(
      raw,
      sig,
      whsec,
      undefined,
      Stripe.createSubtleCryptoProvider(),
    );
  } catch (e) {
    const msg = e instanceof Error ? e.message : "verify failed";
    console.error("Webhook signature verification failed:", msg);
    return new Response(`Webhook Error: ${msg}`, { status: 400 });
  }

  try {
    if (event.type === "checkout.session.completed") {
      const session = event.data.object as Stripe.Checkout.Session;
      const email = session.customer_details?.email;
      console.log("Wira Local purchase:", {
        email,
        customer: session.customer,
        paymentStatus: session.payment_status,
      });
      if (email) {
        // Best-effort — must never fail the webhook (Stripe retries on non-2xx).
        try {
          await sendDownloadEmail(env, email, session.customer_details?.name);
        } catch (e) {
          console.error("Download email failed:", e instanceof Error ? e.message : e);
        }
      }
    }
    return json(200, { received: true });
  } catch (e) {
    const msg = e instanceof Error ? e.message : "handler error";
    console.error("Webhook handler error:", msg);
    return new Response(msg, { status: 500 });
  }
}
