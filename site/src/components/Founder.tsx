import { PRODUCT } from "@/lib/brand";

/** Founder byline block. */
export default function Founder() {
  return (
    <section className="container-narrow py-16">
      <div className="card p-7 sm:p-10 flex flex-col sm:flex-row gap-6 items-start">
        <div
          aria-hidden
          className="flex-none w-16 h-16 rounded-full bg-accent-soft text-accent flex items-center justify-center font-display text-2xl"
        >
          CN
        </div>
        <div>
          <p className="text-lg leading-relaxed">
            “I built {PRODUCT.name} because I wanted an easier way for people to
            get their first real agent without starting from fear. The goal
            isn't another messaging platform. The goal is Hermes, wrapped in a
            friendlier shape, living on your computer, and reached from the
            phone you already trust. Start simple, then grow into the deeper
            stack when you're ready.”
          </p>
          <p className="mt-4 text-sm text-ink-muted">
            — Craig, founder of {PRODUCT.name}. Kenyan, based in {PRODUCT.city}.
          </p>
        </div>
      </div>
    </section>
  );
}
