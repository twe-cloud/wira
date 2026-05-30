/**
 * POST /.netlify/functions/webhook
 * Receives Stripe events. Verify signature before acting on anything.
 *
 * Required env vars:
 *   STRIPE_SECRET_KEY
 *   STRIPE_WHSEC          whsec_... — set after creating the webhook in Stripe dashboard
 *
 * Configure the endpoint in Stripe:
 *   https://your-site.netlify.app/.netlify/functions/webhook
 *   Events to listen for (minimum):
 *     - checkout.session.completed
 *     - customer.subscription.updated
 *     - customer.subscription.deleted
 *     - invoice.payment_failed
 */
import type { Handler } from "@netlify/functions";
import Stripe from "stripe";

export const handler: Handler = async (event) => {
  if (event.httpMethod !== "POST") {
    return { statusCode: 405, body: "Method not allowed" };
  }

  const secret = process.env.STRIPE_SECRET_KEY;
  const whsec = process.env.STRIPE_WHSEC;
  if (!secret || !whsec) {
    console.error("Missing STRIPE_SECRET_KEY or STRIPE_WHSEC");
    return { statusCode: 500, body: "Server not configured" };
  }

  const sig = event.headers["stripe-signature"];
  if (!sig) {
    return { statusCode: 400, body: "Missing stripe-signature header" };
  }

  const stripe = new Stripe(secret);

  let stripeEvent: Stripe.Event;
  try {
    // Netlify gives us the raw body when functions are invoked; if it was
    // base64-encoded (binary), we decode first. Stripe expects the *raw* body.
    const raw = event.isBase64Encoded
      ? Buffer.from(event.body || "", "base64").toString("utf8")
      : event.body || "";
    stripeEvent = stripe.webhooks.constructEvent(raw, sig, whsec);
  } catch (e) {
    const msg = e instanceof Error ? e.message : "verify failed";
    console.error("Webhook signature verification failed:", msg);
    return { statusCode: 400, body: `Webhook Error: ${msg}` };
  }

  try {
    switch (stripeEvent.type) {
      case "checkout.session.completed": {
        const session = stripeEvent.data.object as Stripe.Checkout.Session;
        // TODO(backend): provision this customer's assistant instance.
        //   - look up by session.customer (Stripe customer ID) or session.customer_email
        //   - create their account row
        //   - send the magic link email with onboarding URL
        //   - kick off the WhatsApp QR session
        console.log("New subscriber:", {
          email: session.customer_details?.email,
          customer: session.customer,
          subscription: session.subscription,
        });
        break;
      }
      case "customer.subscription.updated":
      case "customer.subscription.deleted": {
        const sub = stripeEvent.data.object as Stripe.Subscription;
        // TODO(backend): update entitlement so the assistant keeps running
        //   only for active subscriptions.
        console.log("Subscription change:", { id: sub.id, status: sub.status });
        break;
      }
      case "invoice.payment_failed": {
        const inv = stripeEvent.data.object as Stripe.Invoice;
        // TODO(backend): notify the customer and grace-period their instance.
        console.log("Payment failed:", { id: inv.id, customer: inv.customer });
        break;
      }
      default:
        // Acknowledge anything else so Stripe doesn't retry forever.
        break;
    }
    return { statusCode: 200, body: JSON.stringify({ received: true }) };
  } catch (e) {
    const msg = e instanceof Error ? e.message : "handler error";
    console.error("Webhook handler error:", msg);
    return { statusCode: 500, body: msg };
  }
};
