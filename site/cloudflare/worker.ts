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
const DOWNLOAD_URL =
  "https://github.com/twe-cloud/wira/releases/latest/download/Wira.dmg";

interface Env {
  ASSETS: Fetcher;
  STRIPE_SECRET_KEY?: string;
  STRIPE_WHSEC?: string;
  SITE_URL?: string;
  // Optional — best-effort transactional download email. If unset, the buyer
  // still gets the download from the /success page + the Stripe receipt.
  RESEND_API_KEY?: string;
  RESEND_FROM?: string;
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);

    if (url.pathname === "/api/checkout") {
      return handleCheckout(request, env);
    }
    if (url.pathname === "/api/webhook") {
      return handleWebhook(request, env);
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

function json(status: number, body: unknown): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

async function handleCheckout(request: Request, env: Env): Promise<Response> {
  if (request.method !== "POST") {
    return json(405, { error: "Method not allowed" });
  }

  const secret = env.STRIPE_SECRET_KEY;
  const siteUrl = env.SITE_URL || request.headers.get("origin") || "";
  if (!secret) {
    return json(500, { error: "Server is not configured (missing STRIPE_SECRET_KEY)." });
  }
  if (!siteUrl) {
    return json(500, { error: "Server is not configured (missing SITE_URL)." });
  }

  let priceId: string | undefined;
  try {
    ({ priceId } = (await request.json()) as { priceId?: string });
  } catch {
    return json(400, { error: "Invalid JSON body." });
  }
  if (priceId !== WIRA_LOCAL_PRICE) {
    return json(400, { error: "Missing or invalid priceId." });
  }

  const stripe = stripeClient(secret);
  try {
    const session = await stripe.checkout.sessions.create({
      mode: "payment",
      line_items: [{ price: priceId, quantity: 1 }],
      success_url: `${siteUrl}/success?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${siteUrl}/#pricing`,
      allow_promotion_codes: true,
      billing_address_collection: "auto",
      automatic_tax: { enabled: false },
      metadata: { wira_tier: "local", billing_model: "one_time" },
    });
    return json(200, { url: session.url });
  } catch (e) {
    console.error("Stripe checkout error:", e instanceof Error ? e.message : e);
    return json(500, { error: "Could not create checkout session. Please try again." });
  }
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
  const greeting = name ? `Hi ${name},` : "Hi there,";
  const html = `
    <div style="font-family:-apple-system,Segoe UI,Roboto,sans-serif;max-width:520px;margin:0 auto;color:#1a2233">
      <h1 style="font-size:22px;margin:0 0 12px">You're in. Welcome to Wira.</h1>
      <p style="margin:0 0 16px;color:#5f6472">${greeting} thanks for your purchase. Wira is your own AI agent that runs on your Mac and answers you on WhatsApp.</p>
      <p style="margin:0 0 20px">
        <a href="${DOWNLOAD_URL}" style="display:inline-block;background:#6f5318;color:#fff;text-decoration:none;padding:12px 20px;border-radius:10px;font-weight:600">Download Wira for Mac</a>
      </p>
      <p style="margin:0 0 8px;color:#5f6472;font-size:13px">Requires an Apple Silicon Mac (M1 or newer), macOS 12+. Uses your own ChatGPT Plus or Pro subscription as the brain.</p>
      <p style="margin:0 0 8px;color:#5f6472;font-size:13px">After installing: open Wira, click "Sign in with ChatGPT", then scan the WhatsApp code. That's it.</p>
      ${siteUrl ? `<p style="margin:16px 0 0;color:#8d7550;font-size:12px">Need a hand? Just reply to this email, or visit <a href="${siteUrl}/onboarding">${siteUrl}/onboarding</a>.</p>` : ""}
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
