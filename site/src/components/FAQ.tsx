import { motion, AnimatePresence } from "motion/react";
import { useState } from "react";
import { FAQS } from "@/lib/brand";

export default function FAQ() {
  const [open, setOpen] = useState<number | null>(0);

  return (
    <section id="faq" className="container-narrow py-20">
      <h2 className="text-4xl text-center">Honest answers.</h2>
      <p className="mt-3 text-ink-muted text-lg text-center">
        The questions everyone asks before they sign up.
      </p>

      <ul className="mt-10 divide-y divide-border border-y border-border">
        {FAQS.map((f, i) => {
          const isOpen = open === i;
          return (
            <li key={f.q}>
              <button
                onClick={() => setOpen(isOpen ? null : i)}
                aria-expanded={isOpen}
                className="w-full flex items-center justify-between text-left py-5 group"
              >
                <span className="text-lg font-medium pr-4">{f.q}</span>
                <span
                  aria-hidden
                  className={`flex-none w-7 h-7 rounded-full border border-border flex items-center justify-center text-ink-muted transition-transform ${
                    isOpen ? "rotate-45 bg-accent text-white border-accent" : ""
                  }`}
                >
                  +
                </span>
              </button>
              <AnimatePresence initial={false}>
                {isOpen && (
                  <motion.div
                    key="answer"
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    exit={{ opacity: 0, height: 0 }}
                    transition={{ duration: 0.25, ease: [0.22, 1, 0.36, 1] }}
                    className="overflow-hidden"
                  >
                    <p className="pb-5 pr-10 text-ink-muted">{f.a}</p>
                  </motion.div>
                )}
              </AnimatePresence>
            </li>
          );
        })}
      </ul>
    </section>
  );
}
