/**
 * POST /.netlify/functions/checkout
 * Body: { priceId: string }
 * Returns: { url: string } — Stripe-hosted Checkout URL to redirect to.
 *
 * Required env vars (set in Netlify dashboard or .env):
 *   STRIPE_SECRET_KEY        sk_test_... (test) or sk_live_... (prod)
 *   SITE_URL                 https://your-site.netlify.app  (used for success/cancel redirects)
 */
import type { Handler } from "@netlify/functions";
import Stripe from "stripe";

export const handler: Handler = async (event) => {
  if (event.httpMethod !== "POST") {
    return { statusCode: 405, body: "Method not allowed" };
  }

  const secret = process.env.STRIPE_SECRET_KEY;
  const siteUrl = process.env.SITE_URL || event.headers["origin"] || "";
  if (!secret) {
    return jsonError(500, "Server is not configured (missing STRIPE_SECRET_KEY).");
  }
  if (!siteUrl) {
    return jsonError(500, "Server is not configured (missing SITE_URL).");
  }

  let priceId: string | undefined;
  try {
    ({ priceId } = JSON.parse(event.body || "{}"));
  } catch {
    return jsonError(400, "Invalid JSON body.");
  }
  if (!priceId || typeof priceId !== "string" || !priceId.startsWith("price_")) {
    return jsonError(400, "Missing or invalid priceId.");
  }

  const stripe = new Stripe(secret);

  try {
    const session = await stripe.checkout.sessions.create({
      mode: "subscription",
      line_items: [{ price: priceId, quantity: 1 }],
      success_url: `${siteUrl}/success?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${siteUrl}/#pricing`,
      allow_promotion_codes: true,
      billing_address_collection: "auto",
      customer_creation: "always",
      automatic_tax: { enabled: false }, // turn on once you've registered tax IDs
    });

    return {
      statusCode: 200,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: session.url }),
    };
  } catch (e) {
    const msg = e instanceof Error ? e.message : "Unknown error";
    console.error("Stripe checkout error:", msg);
    return jsonError(500, "Could not create checkout session. Please try again.");
  }
};

function jsonError(statusCode: number, error: string) {
  return {
    statusCode,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ error }),
  };
}
