import { AnimatePresence, motion } from "motion/react";
import { useState } from "react";

const INCOMING = "When can you have the draft over to me?";

const TONES: { id: string; label: string; reply: string }[] = [
  {
    id: "warm",
    label: "Warm",
    reply: "Sending it tomorrow morning — I'll ping you the moment it's in your inbox. Hope you've had a good week 🤍",
  },
  {
    id: "brief",
    label: "Brief",
    reply: "Tomorrow AM. Will send.",
  },
  {
    id: "pro",
    label: "Professional",
    reply: "I'll have the draft to you tomorrow morning ahead of close of business. Let me know if you need it sooner.",
  },
  {
    id: "playful",
    label: "Playful",
    reply: "Tomorrow morning, scout's honour 🫡 will be in your inbox before your second coffee.",
  },
];

export default function VoiceToggle() {
  const [tone, setTone] = useState(TONES[0]);

  return (
    <section className="container-prose py-20">
      <div className="grid md:grid-cols-2 gap-10 items-center">
        <div>
          <h2 className="text-4xl">It sounds like you, not like a bot.</h2>
          <p className="mt-3 text-ink-muted text-lg">
            Switch the tone. Same message, four different replies — all of them
            yours. Pick one, mix and match, or let it learn from your last
            twenty chats.
          </p>
          <div
            role="tablist"
            aria-label="Voice tone"
            className="mt-6 inline-flex bg-surface border border-border rounded-full p-1"
          >
            {TONES.map((t) => (
              <button
                key={t.id}
                role="tab"
                aria-selected={tone.id === t.id}
                onClick={() => setTone(t)}
                className={`px-4 py-2 text-sm rounded-full transition-colors ${
                  tone.id === t.id ? "bg-accent text-white" : "text-ink-muted hover:text-ink"
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
              key={tone.id}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -6 }}
              transition={{ duration: 0.22, ease: [0.22, 1, 0.36, 1] }}
              className="self-end max-w-[78%]"
            >
              <div className="bubble-out">{tone.reply}</div>
            </motion.div>
          </AnimatePresence>
        </div>
      </div>
    </section>
  );
}
