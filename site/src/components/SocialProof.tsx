import { PRODUCT } from "@/lib/brand";

/** Pre-testimonial proof: the receipt + the counter. Designed so we look
 *  alive without faking logos. Numbers update once we have telemetry. */
export default function SocialProof() {
  return (
    <section className="border-y border-border bg-surface/60">
      <div className="container-prose py-8 sm:py-10 flex flex-col sm:flex-row items-center justify-between gap-6">
        <div className="flex items-center gap-3">
          <div className="flex -space-x-2">
            {["A", "B", "C", "D", "E", "F"].map((c, i) => (
              <div
                key={c}
                className="w-8 h-8 rounded-full border-2 border-surface flex items-center justify-center text-xs font-medium"
                style={{
                  background: ["#e7f5ec", "#fde9d6", "#e3eafc", "#f4e3f7", "#f7eee3", "#e3f7f1"][i % 6],
                }}
              >
                {c}
              </div>
            ))}
          </div>
          <p className="text-sm text-ink-muted">
            Built for solo operators who want a real agent without having to
            start from terminals and jargon.
          </p>
        </div>
        <p className="text-sm text-ink-muted">
          <span className="text-ink font-medium">{PRODUCT.name}</span> starts on
          WhatsApp, but the real value is the local agent growing underneath.
        </p>
      </div>
    </section>
  );
}
