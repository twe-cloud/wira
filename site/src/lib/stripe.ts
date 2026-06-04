/**
 * Client-side bridge to the Cloudflare Worker that creates a Stripe Checkout
 * Session. Keeps the secret key on the server, redirects the browser to
 * Stripe's hosted page.
 */

export async function startCheckout(priceId: string): Promise<void> {
  const res = await fetch("/api/checkout", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ priceId }),
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
