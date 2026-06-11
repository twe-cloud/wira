import { AnimatePresence, motion } from "motion/react";
import { useEffect, useState } from "react";
import Footer from "@/components/Footer";
import Nav from "@/components/Nav";
import { PRODUCT } from "@/lib/brand";

type State = {
  step: number;
  brainChosen: boolean;
  whatsappPaired: boolean;
  safetyMode: "ask" | "fast";
};

const STORAGE_KEY = "onboarding.v3";

const EMPTY: State = {
  step: 1,
  brainChosen: false,
  whatsappPaired: false,
  safetyMode: "ask",
};

function load(): State {
  if (typeof window === "undefined") return EMPTY;
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return EMPTY;
    return { ...EMPTY, ...JSON.parse(raw) };
  } catch {
    return EMPTY;
  }
}

function save(s: State) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(s));
  } catch {
    /* private mode etc — silently ignore */
  }
}

const STEPS = ["Welcome", "Brain", "WhatsApp", "Safety", "Ready"];

export default function Onboarding() {
  const [state, setState] = useState<State>(load);
  useEffect(() => save(state), [state]);

  const set = <K extends keyof State>(k: K, v: State[K]) =>
    setState((s) => ({ ...s, [k]: v }));
  const next = () => set("step", Math.min(STEPS.length, state.step + 1));
  const back = () => set("step", Math.max(1, state.step - 1));

  return (
    <>
      <Nav hideGetStarted />
      <main className="container-narrow py-12">
        <div className="mb-8 flex items-center gap-2" aria-label="Progress">
          {STEPS.map((label, i) => {
            const n = i + 1;
            const done = n < state.step;
            const active = n === state.step;
            return (
              <div key={label} className="flex flex-1 items-center gap-2">
                <div
                  className={`h-1.5 flex-1 rounded-full ${
                    done || active ? "bg-accent" : "bg-border"
                  }`}
                />
              </div>
            );
          })}
        </div>
        <p className="mb-2 text-sm text-ink-muted">
          Step {state.step} of {STEPS.length} · {STEPS[state.step - 1]}
        </p>

        <AnimatePresence mode="wait">
          <motion.div
            key={state.step}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.22 }}
            className="card p-7"
          >
            {state.step === 1 && <Step1Welcome onNext={next} />}
            {state.step === 2 && <Step2Brain chosen={state.brainChosen} setChosen={(v) => set("brainChosen", v)} onNext={next} onBack={back} />}
            {state.step === 3 && <Step3WhatsApp setPaired={(v) => set("whatsappPaired", v)} onNext={next} onBack={back} />}
            {state.step === 4 && <Step4Safety value={state.safetyMode} setValue={(v) => set("safetyMode", v)} onNext={next} onBack={back} />}
            {state.step === 5 && <Step5Done state={state} onBack={back} />}
          </motion.div>
        </AnimatePresence>

        <p className="mt-6 text-center text-xs text-ink-muted">
          {PRODUCT.name} keeps day one simple: your agent lives on this computer,
          connects to a free or paid brain of your choice, and answers you on
          WhatsApp.
        </p>
      </main>
      <Footer />
    </>
  );
}

function Step1Welcome({
  onNext,
}: {
  onNext: () => void;
}) {
  return (
    <>
      <p className="text-sm font-semibold text-accent">Your agent lives on this computer</p>
      <h2 className="mt-2 text-3xl">Talk to your agent on WhatsApp</h2>
      <p className="mt-2 text-ink-muted">
        Wira sets up a personal agent on this computer, connects it to a brain
        you choose — free, ChatGPT, or fully private — and brings it to
        WhatsApp.
      </p>
      <div className="mt-6 rounded-xl border border-border bg-canvas p-4">
        <div className="font-medium">First, download the app</div>
        <p className="mt-1 text-sm text-ink-muted">
          Wira's public download is Mac-first right now. Download it, drag it to
          Applications, and open it before pairing WhatsApp.
        </p>
        <a href={PRODUCT.downloadMacUrl} className="btn-primary mt-3 inline-flex">
          Download {PRODUCT.name} for Mac
        </a>
        <p className="mt-2 text-xs text-ink-muted">{PRODUCT.systemRequirement}</p>
      </div>
      <div className="mt-6 rounded-xl border border-border bg-canvas p-4 text-sm text-ink-muted">
        Pair the same WhatsApp account you plan to use every day. You do not
        need to register the number here — the real connection happens when you
        scan the QR code inside the Wira app.
      </div>
      <div className="mt-6 flex justify-end">
        <button onClick={onNext} className="btn-primary">
          Set up my agent →
        </button>
      </div>
    </>
  );
}

function Step2Brain({
  chosen,
  setChosen,
  onNext,
  onBack,
}: {
  chosen: boolean;
  setChosen: (v: boolean) => void;
  onNext: () => void;
  onBack: () => void;
}) {
  return (
    <>
      <h2 className="text-3xl">Choose your agent's brain</h2>
      <p className="mt-2 text-ink-muted">
        When you open Wira it asks how it should think. Pick whichever fits you —
        you can switch later.
      </p>
      <div className="mt-6 rounded-xl border border-border bg-accent-soft/40 p-4">
        <div className="text-xs font-semibold text-accent">FASTEST · FREE</div>
        <div className="mt-1 font-medium">Start free in seconds</div>
        <p className="mt-1 text-sm text-ink-muted">
          Sign up free with a service like Groq or DeepSeek, paste the key Wira
          asks for, and start chatting in under a minute. No subscription
          needed — free tiers are enough to get going.
        </p>
        <a
          href="https://console.groq.com/keys"
          target="_blank"
          rel="noreferrer"
          className="mt-3 inline-flex text-sm text-accent underline underline-offset-2"
        >
          Get a free Groq key
        </a>
      </div>
      <div className="mt-3 rounded-xl border border-border bg-accent-soft/20 p-4">
        <div className="text-xs font-semibold text-accent">SIMPLE · USE WHAT YOU HAVE</div>
        <div className="mt-1 font-medium">Connect ChatGPT</div>
        <p className="mt-1 text-sm text-ink-muted">
          Already subscribe to ChatGPT Plus or Pro? Approve Wira on this
          computer in a quick browser step. This lane is experimental — it may
          change or stop working at any time, so if in doubt, start with a free
          key above.
        </p>
      </div>
      <div className="mt-3 rounded-xl border border-border bg-canvas p-4">
        <div className="text-xs font-semibold text-ink-muted">PRIVATE · WHEN THE MACHINE FITS</div>
        <div className="mt-1 font-medium">Run it entirely on this computer</div>
        <p className="mt-1 text-sm text-ink-muted">
          Prefer a fully private path? Install Ollama first, then let Wira use
          it as the brain. Apple Silicon is the strongest fit today; Intel Macs
          and Windows PCs should usually start with the cloud or ChatGPT lane.
        </p>
      </div>
      <div className="mt-4 flex flex-wrap gap-3">
        <button type="button" onClick={() => setChosen(true)} className="btn-primary">
          Got it — I'll choose it in Wira
        </button>
      </div>
      <div className="mt-6 flex justify-between">
        <button onClick={onBack} className="btn-ghost">Back</button>
        <button onClick={onNext} className="btn-primary" disabled={!chosen}>
          Continue →
        </button>
      </div>
    </>
  );
}

function Step3WhatsApp({
  setPaired,
  onNext,
  onBack,
}: {
  setPaired: (v: boolean) => void;
  onNext: () => void;
  onBack: () => void;
}) {
  return (
    <>
      <h2 className="text-3xl">Connect WhatsApp</h2>
      <p className="mt-2 text-ink-muted">
        Pairing uses WhatsApp's Linked Devices, like adding a computer. Once
        paired, WhatsApp becomes the easiest way to talk to Wira while the agent
        runs on this computer.
      </p>
      <div className="mt-6 rounded-xl border border-border bg-accent-soft/20 p-4 text-sm text-ink-muted">
        Make sure Wira is open on your Mac first — the QR code appears in the app window.
      </div>
      <ol className="mt-4 space-y-3 text-sm text-ink-muted">
        <li><strong className="text-ink">1.</strong> Open WhatsApp on your phone.</li>
        <li><strong className="text-ink">2.</strong> Go to Settings → Linked Devices.</li>
        <li><strong className="text-ink">3.</strong> Tap Link a Device.</li>
        <li><strong className="text-ink">4.</strong> Scan the code shown in the Wira window.</li>
      </ol>
      <div className="mt-6 rounded-xl border border-border bg-canvas p-4 text-sm text-ink-muted">
        When the code is scanned, start with something Wira can do right away —
        like “what's in my Downloads folder?” or “find the latest invoice PDF.”
      </div>
      <div className="mt-6 flex justify-between">
        <button onClick={onBack} className="btn-ghost">Back</button>
        <button onClick={() => { setPaired(true); onNext(); }} className="btn-primary">
          WhatsApp is connected →
        </button>
      </div>
    </>
  );
}

function Step4Safety({
  value,
  setValue,
  onNext,
  onBack,
}: {
  value: State["safetyMode"];
  setValue: (v: State["safetyMode"]) => void;
  onNext: () => void;
  onBack: () => void;
}) {
  const options: { id: State["safetyMode"]; title: string; body: string }[] = [
    {
      id: "ask",
      title: "Ask before risky actions",
      body: "Best first setting. Wira can help freely, but pauses before purchases, deletes, public sends, or anything unclear.",
    },
    {
      id: "fast",
      title: "Move faster on normal work",
      body: "Good once you trust the flow. Wira still pauses for destructive, expensive, public, or sensitive actions.",
    },
  ];

  return (
    <>
      <h2 className="text-3xl">Choose the safety posture</h2>
      <p className="mt-2 text-ink-muted">
        Wira is owner-controlled by default. You decide how cautious it should
        be when a task could change something important.
      </p>
      <div className="mt-6 space-y-3">
        {options.map((o) => (
          <label
            key={o.id}
            className={`block cursor-pointer rounded-xl border p-4 transition-colors ${
              value === o.id ? "border-accent bg-accent-soft/50" : "border-border bg-canvas"
            }`}
          >
            <input
              type="radio"
              name="safety"
              checked={value === o.id}
              onChange={() => setValue(o.id)}
              className="sr-only"
            />
            <div className="font-medium">{o.title}</div>
            <div className="mt-1 text-sm text-ink-muted">{o.body}</div>
          </label>
        ))}
      </div>
      <div className="mt-6 flex justify-between">
        <button onClick={onBack} className="btn-ghost">Back</button>
        <button onClick={onNext} className="btn-primary">Continue →</button>
      </div>
    </>
  );
}

function Step5Done({ state, onBack }: { state: State; onBack: () => void }) {
  return (
    <>
      <div className="inline-flex h-12 w-12 items-center justify-center rounded-full bg-accent-soft text-xl text-accent">
        ✓
      </div>
      <h2 className="mt-4 text-3xl">Your agent is ready</h2>
      <p className="mt-2 text-ink-muted">
        Open WhatsApp and send Wira the first real message. Keep it simple:
        ask for a summary, ask it to find a file, or ask it to make a plan.
      </p>
      <div className="mt-6 rounded-xl border border-border bg-canvas p-4 text-sm">
        <div className="mb-2 font-medium">Ready for first message</div>
        <ul className="space-y-2 text-ink-muted">
          <li>• “What's in my Downloads folder?”</li>
          <li>• “Find my latest invoice PDF.”</li>
          <li>• “Make a shipping plan for this project.”</li>
          <li>• “What time is it in Dallas?”</li>
        </ul>
        <div className="mt-4 text-xs text-ink-muted">
          Next: open Wira on your Mac, choose the same safety mode there, then
          send your first WhatsApp command. Safety: {state.safetyMode === "ask" ? "ask first" : "move fast carefully"}
        </div>
      </div>
      <div className="mt-6 flex justify-between">
        <button onClick={onBack} className="btn-ghost">Back</button>
        <a href={PRODUCT.downloadMacUrl} className="btn-primary">Download / reopen Wira →</a>
      </div>
    </>
  );
}
