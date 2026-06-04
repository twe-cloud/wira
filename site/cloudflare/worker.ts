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

interface Env {
  ASSETS: Fetcher;
  STRIPE_SECRET_KEY?: string;
  STRIPE_WHSEC?: string;
  SITE_URL?: string;
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
      // TODO(backend): provision this customer's Wira Local instance.
      console.log("Wira Local purchase:", {
        email: session.customer_details?.email,
        customer: session.customer,
        paymentStatus: session.payment_status,
      });
    }
    return json(200, { received: true });
  } catch (e) {
    const msg = e instanceof Error ? e.message : "handler error";
    console.error("Webhook handler error:", msg);
    return new Response(msg, { status: 500 });
  }
}
