import { motion } from "motion/react";
import { PRODUCT } from "@/lib/brand";
import PhoneMockup from "./PhoneMockup";

export default function Hero() {
  return (
    <section className="container-prose pt-12 pb-16 sm:pt-20 sm:pb-24">
      <div className="grid lg:grid-cols-2 gap-12 items-center">
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
        >
          <div className="inline-flex items-center gap-2 bg-accent-soft text-accent rounded-full px-3 py-1 text-xs font-medium">
            <span className="inline-block w-1.5 h-1.5 rounded-full bg-accent" /> Live on your personal WhatsApp
          </div>
          <h1 className="mt-5 text-5xl sm:text-6xl leading-[1.02]">
            Your WhatsApp,
            <br />
            <em className="italic">finally answered.</em>
          </h1>
          <p className="mt-5 text-lg text-ink-muted max-w-xl">
            {PRODUCT.name} is the assistant that replies on your number, in your
            voice, while you work — and only pings you for the messages that
            actually need you.
          </p>
          <div className="mt-7 flex items-center gap-3 flex-wrap">
            <a href="#pricing" className="btn-primary">
              Get started — 5 min setup
            </a>
            <a href="#how" className="btn-ghost">
              How it works
            </a>
          </div>
          <p className="mt-4 text-xs text-ink-muted">
            Pair via QR code · Cancel anytime · Your chats stay yours.
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1], delay: 0.1 }}
        >
          <PhoneMockup />
        </motion.div>
      </div>
    </section>
  );
}
