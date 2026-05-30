import { useState } from "react";
import { PRICING, PRODUCT } from "@/lib/brand";
import { startCheckout } from "@/lib/stripe";

export default function Pricing() {
  const [annual, setAnnual] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const tier = annual ? PRICING.annual : PRICING.monthly;
  const priceId = annual ? PRICING.stripePriceAnnual : PRICING.stripePriceMonthly;

  async function handleBuy() {
    setError(null);
    setLoading(true);
    try {
      await startCheckout(priceId);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong. Please try again.");
      setLoading(false);
    }
  }

  return (
    <section id="pricing" className="container-prose py-20">
      <div className="max-w-2xl mx-auto text-center">
        <h2 className="text-4xl">One price. No upsell.</h2>
        <p className="mt-3 text-ink-muted text-lg">
          Cancel anytime. Includes everything {PRODUCT.name} does today and
          everything we ship next.
        </p>
      </div>

      <div className="mt-8 flex justify-center">
        <div
          role="tablist"
          aria-label="Billing cycle"
          className="inline-flex bg-surface border border-border rounded-full p-1"
        >
          <button
            role="tab"
            aria-selected={!annual}
            onClick={() => setAnnual(false)}
            className={`px-5 py-2 text-sm rounded-full ${
              !annual ? "bg-accent text-white" : "text-ink-muted"
            }`}
          >
            Monthly
          </button>
          <button
            role="tab"
            aria-selected={annual}
            onClick={() => setAnnual(true)}
            className={`px-5 py-2 text-sm rounded-full ${
              annual ? "bg-accent text-white" : "text-ink-muted"
            }`}
          >
            Annual <span className="ml-1 text-accent">·</span>
            <span className={`ml-1 text-xs ${annual ? "text-white/90" : "text-accent"}`}>
              {PRICING.annual.saveLabel}
            </span>
          </button>
        </div>
      </div>

      <div className="mt-10 max-w-lg mx-auto card p-8">
        <div className="flex items-baseline gap-2">
          <span className="font-display text-6xl text-ink">{tier.label}</span>
          <span className="text-ink-muted">{tier.per}</span>
        </div>
        <p className="mt-1 text-sm text-ink-muted">
          Billed {annual ? "yearly" : "monthly"} · USD · cancel from your account at any time
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

        <button
          onClick={handleBuy}
          disabled={loading}
          className="btn-primary w-full mt-7"
        >
          {loading ? "Redirecting to Stripe…" : `Start with ${PRODUCT.name}`}
        </button>
        {error && (
          <p className="mt-3 text-sm text-danger" role="alert">
            {error}
          </p>
        )}
        <p className="mt-3 text-xs text-ink-muted text-center">
          Secure checkout by Stripe · You'll be back here in 30 seconds.
        </p>
      </div>
    </section>
  );
}
