import { AnimatePresence, motion } from "motion/react";
import { useEffect, useState } from "react";

type Turn = { from: "them" | "you"; text: string; pause?: number };

const SCENES: { who: string; turns: Turn[] }[] = [
  {
    who: "Vera · your private agent",
    turns: [
      { from: "them", text: "What meetings do I have after 2pm today?" },
      { from: "you", text: "You have a client check-in at 3:30 PM and a design review at 5 PM. Want a shorter briefing for both?" },
    ],
  },
  {
    who: "Vera · your private agent",
    turns: [
      { from: "them", text: "Search this machine for the latest invoice PDF." },
      { from: "you", text: "Found the newest invoice PDF in Downloads. I can open it, summarize it, or prep an email around it next." },
    ],
  },
  {
    who: "Vera · your private agent",
    turns: [
      { from: "them", text: "Give me a plan for shipping this feature tonight." },
      { from: "you", text: "I can do that. I'll break it into implementation slices, risks, and a first execution order so you can move immediately." },
    ],
  },
];

const EASE = [0.22, 1, 0.36, 1] as const;

function useReducedMotion() {
  const [reduced, setReduced] = useState(false);
  useEffect(() => {
    const m = window.matchMedia("(prefers-reduced-motion: reduce)");
    setReduced(m.matches);
    const onChange = () => setReduced(m.matches);
    m.addEventListener?.("change", onChange);
    return () => m.removeEventListener?.("change", onChange);
  }, []);
  return reduced;
}

export default function PhoneMockup() {
  const reduced = useReducedMotion();
  const [sceneIdx, setSceneIdx] = useState(0);
  const [turnIdx, setTurnIdx] = useState(0);
  const [typing, setTyping] = useState(false);

  useEffect(() => {
    if (reduced) return;
    const scene = SCENES[sceneIdx];
    const t = scene.turns[turnIdx];
    if (!t) {
      const id = setTimeout(() => {
        setSceneIdx((i) => (i + 1) % SCENES.length);
        setTurnIdx(0);
      }, 2400);
      return () => clearTimeout(id);
    }
    if (t.from === "you") {
      setTyping(true);
      const id = setTimeout(() => {
        setTyping(false);
        setTurnIdx((i) => i + 1);
      }, 900 + Math.min(2200, t.text.length * 22));
      return () => clearTimeout(id);
    } else {
      const id = setTimeout(() => setTurnIdx((i) => i + 1), 1300);
      return () => clearTimeout(id);
    }
  }, [sceneIdx, turnIdx, reduced]);

  const scene = SCENES[sceneIdx];
  const visibleTurns = reduced ? scene.turns : scene.turns.slice(0, turnIdx);

  return (
    <div
      className="relative mx-auto"
      style={{ width: 320, maxWidth: "100%" }}
      aria-label="Animated example: the owner messages Vera, the local agent responds with real work context."
    >
      <div
        className="bg-ink rounded-[44px] p-3 shadow-2xl"
        style={{ boxShadow: "0 30px 60px -20px rgba(14,20,19,.35)" }}
      >
        <div className="bg-canvas rounded-[34px] overflow-hidden" style={{ height: 580 }}>
          <div className="flex items-center justify-between px-5 pt-3 pb-1 text-[11px] text-ink-muted">
            <span>9:41</span>
            <div className="flex items-center gap-1.5">
              <span className="inline-block w-3 h-1.5 rounded-sm bg-ink-muted/60" />
              <span className="inline-block w-3 h-1.5 rounded-sm bg-ink-muted/60" />
              <span className="inline-block w-5 h-2.5 rounded-sm border border-ink-muted/60" />
            </div>
          </div>

          <div className="flex items-center gap-3 px-4 py-3 border-b border-border">
            <div className="w-9 h-9 rounded-full bg-accent-soft text-accent flex items-center justify-center font-medium">
              V
            </div>
            <div className="flex-1">
              <div className="text-sm font-medium leading-tight">{scene.who}</div>
              <div className="text-[11px] text-accent">local agent connected</div>
            </div>
          </div>

          <div className="px-4 py-4 flex flex-col gap-2 overflow-hidden" style={{ height: 460 }}>
            <AnimatePresence initial={false} mode="popLayout">
              {visibleTurns.map((t, i) => (
                <motion.div
                  key={`${sceneIdx}-${i}`}
                  initial={{ opacity: 0, y: 8, scale: 0.98 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  transition={{ duration: 0.28, ease: EASE }}
                  className={t.from === "you" ? "self-end" : "self-start"}
                >
                  <div className={t.from === "you" ? "bubble-out" : "bubble-in"}>
                    {t.text}
                  </div>
                </motion.div>
              ))}
              {typing && (
                <motion.div
                  key={`${sceneIdx}-typing`}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.2 }}
                  className="self-end"
                >
                  <div className="bubble-out !py-3 !px-4 flex items-center gap-1">
                    {[0, 1, 2].map((d) => (
                      <motion.span
                        key={d}
                        className="inline-block w-1.5 h-1.5 rounded-full bg-white/80"
                        animate={{ y: [0, -3, 0] }}
                        transition={{ duration: 0.9, repeat: Infinity, delay: d * 0.15, ease: "easeInOut" }}
                      />
                    ))}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>

      <div
        className="absolute -right-3 top-20 bg-surface border border-border rounded-full px-3 py-1 text-xs font-medium shadow-sm"
        aria-hidden
      >
        <span className="text-accent">●</span> local agent active
      </div>
    </div>
  );
}
