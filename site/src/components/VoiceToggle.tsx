import { AnimatePresence, motion } from "motion/react";
import { useState } from "react";

const INCOMING = "Search my Downloads for the latest invoice PDF and tell me what you find.";

const MODES: { id: string; label: string; reply: string }[] = [
  {
    id: "quick",
    label: "Quick win",
    reply: "Found two invoice PDFs from today in Downloads. The newest is Invoice-7842.pdf modified at 11:14 AM.",
  },
  {
    id: "guided",
    label: "Guided",
    reply: "I found the newest invoice PDF in Downloads. Want me to open it next or summarize the filename + modified time only?",
  },
  {
    id: "operator",
    label: "Operator",
    reply: "Scanned Downloads and found the newest invoice PDF. I can move it, summarize it, or prep an email around it if you want the next step.",
  },
  {
    id: "advanced",
    label: "Advanced path",
    reply: "Found the file locally. This is the same kind of task you can later run from Hermes Desktop or CLI once you're ready for the deeper surfaces.",
  },
];

export default function VoiceToggle() {
  const [mode, setMode] = useState(MODES[0]);

  return (
    <section className="container-prose py-20">
      <div className="grid md:grid-cols-2 gap-10 items-center">
        <div>
          <h2 className="text-4xl">Start from the phone. Grow into the stack.</h2>
          <p className="mt-3 text-ink-muted text-lg">
            Wira should feel simple first: message your agent from WhatsApp and
            get real work done. Under that friendly surface is a path into the
            fuller Hermes world when you want more power.
          </p>
          <div
            role="tablist"
            aria-label="Agent mode"
            className="mt-6 inline-flex bg-surface border border-border rounded-full p-1 flex-wrap"
          >
            {MODES.map((t) => (
              <button
                key={t.id}
                role="tab"
                aria-selected={mode.id === t.id}
                onClick={() => setMode(t)}
                className={`px-4 py-2 text-sm rounded-full transition-colors ${
                  mode.id === t.id ? "bg-accent text-white" : "text-ink-muted hover:text-ink"
                }`}
              >
                {t.label}
              </button>
            ))}
          </div>
        </div>

        <div className="card p-5 flex flex-col gap-2">
          <div className="bubble-in">{INCOMING}</div>
          <AnimatePresence mode="wait">
            <motion.div
              key={mode.id}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -6 }}
              transition={{ duration: 0.22, ease: [0.22, 1, 0.36, 1] }}
              className="self-end max-w-[78%]"
            >
              <div className="bubble-out">{mode.reply}</div>
            </motion.div>
          </AnimatePresence>
        </div>
      </div>
    </section>
  );
}
