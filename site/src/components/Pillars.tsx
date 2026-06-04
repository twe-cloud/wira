import { motion } from "motion/react";
import { PILLARS } from "@/lib/brand";

export default function Pillars() {
  return (
    <section id="features" className="container-prose py-20">
      <div className="max-w-2xl">
        <h2 className="text-4xl">Three things, done well.</h2>
        <p className="mt-3 text-ink-muted text-lg">
          Not another dashboard. Not another chat toy. A branded doorway into a
          real agent that can grow with the operator using it.
        </p>
      </div>
      <div className="mt-12 grid md:grid-cols-3 gap-5">
        {PILLARS.map((p, i) => (
          <motion.div
            key={p.name}
            initial={{ opacity: 0, y: 12 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-80px" }}
            transition={{ duration: 0.45, ease: [0.22, 1, 0.36, 1], delay: i * 0.08 }}
            className="card p-7"
          >
            <div className="text-xs font-medium text-accent uppercase tracking-wider">
              0{i + 1}
            </div>
            <h3 className="mt-2 text-2xl">{p.name}</h3>
            <p className="mt-3 text-ink-muted">{p.body}</p>
          </motion.div>
        ))}
      </div>
    </section>
  );
}
