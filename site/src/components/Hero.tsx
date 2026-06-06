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
            <span className="inline-block w-1.5 h-1.5 rounded-full bg-accent" /> Phone-first access to your local agent
          </div>
          <h1 className="mt-5 text-5xl sm:text-6xl leading-[1.02]">
            Your first personal agent,
            <br />
            <em className="italic">reached from WhatsApp.</em>
          </h1>
          <p className="mt-5 text-lg text-ink-muted max-w-xl">
            {PRODUCT.name} sets up a personal agent on your computer and lets
            you reach it from WhatsApp. Start simple, then grow into deeper
            agentic work when you're ready.
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
            {PRODUCT.heroSupportLine}
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
