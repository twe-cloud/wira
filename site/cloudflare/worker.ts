/**
 * Wira site Worker (Cloudflare).
 *
 * Serves the built Vite SPA from the ASSETS binding and handles the two
 * Stripe API routes that used to live in Netlify Functions:
 *   POST /api/checkout  — create a Stripe Checkout Session
 *   POST /api/webhook   — receive + verify Stripe webhook events
 *
 * Static assets are served directly by the assets runtime; this Worker only
 * runs first for `/api/*` and `/download/*` (see wrangler.jsonc run_worker_first).
 *
 * Pure/testable helpers live in ./worker-lib so this entry module only exports
 * the default handler (the Workers runtime rejects other named exports here).
 */
import Stripe from "stripe";
import {
  CHECKOUT_PRODUCT_DESCRIPTION,
  CHECKOUT_PRODUCT_NAME,
  DOWNLOADS,
  LEGACY_DOWNLOAD_PATHS,
  WIRA_LOCAL_PRICE,
  corsHeaders,
  defaultDownloadUrl,
  envDownloadOverride,
  json,
  publicDownloadUrl,
  sanitizeSiteBase,
  type DownloadSpec,
  type Env,
} from "./worker-lib";

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);

    if (url.pathname === "/api/checkout") {
      if (request.method === "OPTIONS") {
        return new Response(null, { status: 204, headers: corsHeaders(request.headers.get("origin"), env) });
      }
      return handleCheckout(request, env);
    }
    if (url.pathname === "/api/webhook") {
      return handleWebhook(request, env);
    }
    if (url.pathname === DOWNLOADS.mac.path) {
      return handleDownload(request, env, DOWNLOADS.mac);
    }
    if (url.pathname === DOWNLOADS.windows.path) {
      return handleDownload(request, env, DOWNLOADS.windows);
    }
    const legacy = LEGACY_DOWNLOAD_PATHS[url.pathname];
    if (legacy) {
      return handleDownload(request, env, DOWNLOADS[legacy]);
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

function handleDownload(request: Request, _env: Env, spec: DownloadSpec): Response {
  if (request.method !== "GET" && request.method !== "HEAD") {
    return new Response("Method not allowed", {
      status: 405,
      headers: { Allow: "GET, HEAD" },
    });
  }
  // Redirect to the current GitHub release asset instead of proxying the bytes.
  // Proxying let Cloudflare edge-cache the response by path (query-ignored,
  // unpurgeable on workers.dev), so a replaced asset served stale for a day.
  // GitHub's "latest/download" always points at the current (signed) build, and
  // the short-lived redirect is safe to cache because the target is stable.
  const target = envDownloadOverride(_env, spec) || defaultDownloadUrl(spec);
  return new Response(null, {
    status: 302,
    headers: {
      Location: target,
      "Cache-Control": "public, max-age=300",
    },
  });
}

async function handleCheckout(request: Request, env: Env): Promise<Response> {
  const origin = request.headers.get("origin");
  const cors = corsHeaders(origin, env);

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
  const macUrl = publicDownloadUrl(env, DOWNLOADS.mac, siteUrl);
  const windowsUrl = publicDownloadUrl(env, DOWNLOADS.windows, siteUrl);
  const greeting = name ? `Hi ${name},` : "Hi there,";
  const html = `
    <div style="font-family:-apple-system,Segoe UI,Roboto,sans-serif;max-width:520px;margin:0 auto;color:#1a2233">
      <h1 style="font-size:22px;margin:0 0 12px">You're in. Welcome to Wira.</h1>
      <p style="margin:0 0 16px;color:#5f6472">${greeting} thanks for your purchase. Wira is your own AI agent that runs on your computer and answers you on WhatsApp.</p>
      <p style="margin:0 0 12px">
        <a href="${macUrl}" style="display:inline-block;background:#6f5318;color:#fff;text-decoration:none;padding:12px 20px;border-radius:10px;font-weight:600">Download Wira for Mac</a>
      </p>
      <p style="margin:0 0 16px;color:#5f6472;font-size:13px">On Windows? <a href="${windowsUrl}" style="color:#6f5318">Download the Windows app (early beta)</a>. It isn't code-signed yet, so Windows may show a SmartScreen warning — choose More info, then Run anyway.</p>
      <p style="margin:0 0 8px;color:#5f6472;font-size:13px">After installing: open Wira, choose how it should think, then scan the WhatsApp QR code. Start free, use ChatGPT, or keep the brain private when your machine is a good fit. Three steps and your agent is live.</p>
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
      subject: "Your Wira download — install on Mac or Windows",
      html,
    }),
  });
  if (!resp.ok) {
    throw new Error(`Resend ${resp.status}: ${await resp.text()}`);
  }
  // No buyer PII in logs — just the outcome.
  console.log("Download email sent", { ok: true });
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
      // Don't log buyer PII (email / customer id) — just the outcome.
      console.log("Wira Local purchase:", {
        paymentStatus: session.payment_status,
        hasEmail: Boolean(email),
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
