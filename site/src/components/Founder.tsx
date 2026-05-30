import { PRODUCT } from "@/lib/brand";

/**
 * Pre-testimonial trust block. The marketing brief calls this out as the
 * "byline wall" social-proof angle. Replace the placeholder copy and avatar
 * with the real founder before launch.
 */
export default function Founder() {
  return (
    <section className="container-narrow py-16">
      <div className="card p-7 sm:p-10 flex flex-col sm:flex-row gap-6 items-start">
        <div
          aria-hidden
          className="flex-none w-16 h-16 rounded-full bg-accent-soft text-accent flex items-center justify-center font-display text-3xl"
        >
          C
        </div>
        <div>
          <p className="text-lg leading-relaxed">
            “I built {PRODUCT.name} because I lost my Sundays to WhatsApp.
            Clients, leads, family, group chats — all on one screen, all
            wanting an answer. It wasn't sustainable, and the alternatives
            (mute, ignore, hire someone) all felt worse. So I made the thing
            I wanted: an assistant that lives where I am, sounds like me, and
            taps me only when it's actually me they need.”
          </p>
          <p className="mt-4 text-sm text-ink-muted">
            — Craig, founder of {PRODUCT.name}. Based in {PRODUCT.city}.
          </p>
        </div>
      </div>
    </section>
  );
}
