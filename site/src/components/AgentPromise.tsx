import { motion } from "motion/react";
import { AGENT_PROMISES, AGENT_PULLS, PRODUCT } from "@/lib/brand";

export default function AgentPromise() {
  return (
    <section id="promise" className="container-prose py-20">
      <div className="grid gap-10 lg:grid-cols-[0.95fr_1.05fr] lg:items-start">
        <div>
          <div className="inline-flex items-center gap-2 rounded-full bg-accent-soft px-3 py-1 text-xs font-medium text-accent">
            <span className="inline-block h-1.5 w-1.5 rounded-full bg-accent" />
            Why keep {PRODUCT.name} on your WhatsApp?
          </div>
          <h2 className="mt-5 text-4xl">A familiar thread that turns into real leverage.</h2>
          <p className="mt-4 text-lg text-ink-muted">
            On day one, the appeal is simple: you can message your agent from WhatsApp.
            After that, the value shifts. {PRODUCT.name} starts holding onto useful context,
            picking up your patterns, and making repeat tasks easier to hand off.
          </p>
          <p className="mt-4 text-lg text-ink-muted">
            That is the point. You are not installing another chat app. You are building a working relationship with an agent that becomes more useful as it gets to know your world.
          </p>
        </div>

        <div className="card p-6 sm:p-8">
          <div className="text-sm font-medium text-ink">What that feels like over time</div>
          <ul className="mt-5 space-y-4">
            {AGENT_PULLS.map((pull) => (
              <li key={pull} className="flex gap-3 text-ink-muted">
                <span className="mt-1 inline-flex h-5 w-5 flex-none items-center justify-center rounded-full bg-accent/10 text-[11px] font-semibold text-accent">
                  ✓
                </span>
                <span>{pull}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className="mt-12 grid gap-5 md:grid-cols-2">
        {AGENT_PROMISES.map((item, index) => (
          <motion.div
            key={item.name}
            initial={{ opacity: 0, y: 12 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-80px" }}
            transition={{ duration: 0.45, ease: [0.22, 1, 0.36, 1], delay: index * 0.06 }}
            className="card p-7"
          >
            <div className="text-xs font-medium uppercase tracking-wider text-accent">
              0{index + 1}
            </div>
            <h3 className="mt-2 text-2xl">{item.name}</h3>
            <p className="mt-3 text-ink-muted">{item.body}</p>
          </motion.div>
        ))}
      </div>
    </section>
  );
}
