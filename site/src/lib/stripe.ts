/**
 * Client-side bridge to the Cloudflare Worker that creates a Stripe Checkout
 * Session. Keeps the secret key on the server, redirects the browser to
 * Stripe's hosted page.
 */

const API_BASE = (import.meta.env.VITE_CHECKOUT_API_BASE || "").replace(/\/$/, "");
const SITE_BASE = `${window.location.origin}${(import.meta.env.BASE_URL || "/").replace(/\/$/, "")}`;

export async function startCheckout(priceId: string): Promise<void> {
  const endpoint = `${API_BASE}/api/checkout`;
  const res = await fetch(endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ priceId, siteBase: SITE_BASE }),
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`Checkout failed (${res.status}): ${text}`);
  }
  const data = (await res.json()) as { url?: string; error?: string };
  if (!data.url) {
    throw new Error(data.error || "Checkout returned no redirect URL");
  }
  window.location.href = data.url;
}
