import { PRODUCT } from "@/lib/brand";

/** Founder byline block. */
export default function Founder() {
  return (
    <section className="container-narrow py-16">
      <div className="card p-7 sm:p-10">
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
            — Twe, founder of {PRODUCT.name}.
          </p>
        </div>
      </div>
    </section>
  );
}
