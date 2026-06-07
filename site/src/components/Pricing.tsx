import { useState } from "react";
import { PRICING, PRODUCT } from "@/lib/brand";
import { startCheckout } from "@/lib/stripe";

export default function Pricing() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleBuy() {
    setError(null);
    setLoading(true);
    try {
      await startCheckout(PRICING.stripePriceLocal);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong. Please try again.");
      setLoading(false);
    }
  }

  return (
    <section id="pricing" className="container-prose py-20">
      <div className="max-w-2xl mx-auto text-center">
        <h2 className="text-4xl">Buy once. Install once. Wira is yours locally.</h2>
        <p className="mt-3 text-ink-muted text-lg">
          Wira Local is a one-time setup purchase for the agent that runs on your
          computer. No monthly fee for the local install. Mac download is live now,
          Windows is in early beta, and Apple Silicon is the best fit for fully
          private local AI.
        </p>
      </div>

      <div className="mt-10 max-w-lg mx-auto card p-8">
        <div className="flex items-baseline gap-2">
          <span className="font-display text-6xl text-ink">{PRICING.local.label}</span>
          <span className="text-ink-muted">{PRICING.local.per}</span>
        </div>
        <p className="mt-1 text-sm text-ink-muted">
          One-time Wira Local purchase · USD · after install, the local app is yours
        </p>

        <ul className="mt-6 space-y-3">
          {PRICING.includes.map((line) => (
            <li key={line} className="flex items-start gap-3 text-ink">
              <span
                aria-hidden
                className="mt-1.5 inline-block w-2 h-2 rounded-full bg-accent flex-none"
              />
              <span>{line}</span>
            </li>
          ))}
        </ul>

        <div className="mt-6 rounded-xl border border-border bg-canvas p-4 text-sm text-ink-muted">
          The $49 pays for the Wira Local app and guided setup path. The AI
          brain is separate: free tiers are enough to start, and any paid
          ChatGPT or API-provider cost only applies if you choose it.
        </div>

        <button
          onClick={handleBuy}
          disabled={loading}
          className="btn-primary w-full mt-7"
        >
          {loading ? "Redirecting to Stripe…" : `Buy ${PRODUCT.name} Local`}
        </button>
        {error && (
          <p className="mt-3 text-sm text-danger" role="alert">
            {error}
          </p>
        )}
        <p className="mt-3 text-xs text-ink-muted text-center">
          {PRODUCT.pricingSupportLine}
        </p>
        <p className="mt-2 text-xs text-ink-muted text-center">
          {PRODUCT.systemRequirement} Start free in seconds, connect ChatGPT, or
          keep the brain private when your machine is a good fit.
        </p>
      </div>
    </section>
  );
}
