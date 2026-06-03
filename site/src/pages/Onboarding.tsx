import { AnimatePresence, motion } from "motion/react";
import { useEffect, useState } from "react";
import Footer from "@/components/Footer";
import Nav from "@/components/Nav";
import { PRODUCT } from "@/lib/brand";

type State = {
  step: number;
  phone: string;
  chatgptConnected: boolean;
  whatsappPaired: boolean;
  safetyMode: "ask" | "fast";
};

const STORAGE_KEY = "onboarding.v2";

const EMPTY: State = {
  step: 1,
  phone: "",
  chatgptConnected: false,
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

const STEPS = ["Welcome", "ChatGPT", "WhatsApp", "Safety", "Ready"];

export default function Onboarding() {
  const [state, setState] = useState<State>(load);
  useEffect(() => save(state), [state]);

  const set = <K extends keyof State>(k: K, v: State[K]) =>
    setState((s) => ({ ...s, [k]: v }));
  const next = () => set("step", Math.min(STEPS.length, state.step + 1));
  const back = () => set("step", Math.max(1, state.step - 1));

  return (
    <>
      <Nav />
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
            {state.step === 1 && <Step1Welcome phone={state.phone} setPhone={(v) => set("phone", v)} onNext={next} />}
            {state.step === 2 && <Step2ChatGPT connected={state.chatgptConnected} setConnected={(v) => set("chatgptConnected", v)} onNext={next} onBack={back} />}
            {state.step === 3 && <Step3WhatsApp setPaired={(v) => set("whatsappPaired", v)} onNext={next} onBack={back} />}
            {state.step === 4 && <Step4Safety value={state.safetyMode} setValue={(v) => set("safetyMode", v)} onNext={next} onBack={back} />}
            {state.step === 5 && <Step5Done state={state} onBack={back} />}
          </motion.div>
        </AnimatePresence>

        <p className="mt-6 text-center text-xs text-ink-muted">
          {PRODUCT.name} keeps day one simple: your agent lives on this computer,
          connects to ChatGPT, and answers you on WhatsApp.
        </p>
      </main>
      <Footer />
    </>
  );
}

function Step1Welcome({
  phone,
  setPhone,
  onNext,
}: {
  phone: string;
  setPhone: (v: string) => void;
  onNext: () => void;
}) {
  return (
    <>
      <p className="text-sm font-semibold text-accent">Your agent lives on this computer</p>
      <h2 className="mt-2 text-3xl">Talk to your agent on WhatsApp</h2>
      <p className="mt-2 text-ink-muted">
        Wira sets up a personal agent on this computer, connects it to the
        ChatGPT subscription you already have, and brings it to WhatsApp.
      </p>
      <label className="mt-6 block text-sm font-medium">Your WhatsApp number</label>
      <input
        type="tel"
        inputMode="tel"
        autoComplete="tel"
        placeholder="+254 700 000 000"
        value={phone}
        onChange={(e) => setPhone(e.target.value)}
        className="mt-2 w-full rounded-xl border border-border bg-canvas px-4 py-3 text-base focus:outline-none"
      />
      <p className="mt-2 text-xs text-ink-muted">
        This is the phone number you will use to reach Wira after pairing.
      </p>
      <div className="mt-6 flex justify-end">
        <button disabled={!phone.trim()} onClick={onNext} className="btn-primary disabled:opacity-40">
          Set up my agent →
        </button>
      </div>
    </>
  );
}

function Step2ChatGPT({
  connected,
  setConnected,
  onNext,
  onBack,
}: {
  connected: boolean;
  setConnected: (v: boolean) => void;
  onNext: () => void;
  onBack: () => void;
}) {
  return (
    <>
      <h2 className="text-3xl">Connect ChatGPT</h2>
      <p className="mt-2 text-ink-muted">
        Wira uses the ChatGPT account you already pay for. If ChatGPT asks for
        a quick permission, follow the browser step, then come back here.
      </p>
      <div className="mt-6 rounded-xl border border-border bg-canvas p-4">
        <div className="font-medium">One quick permission is needed</div>
        <p className="mt-1 text-sm text-ink-muted">
          Open ChatGPT, approve Wira on this computer, then try again if the
          browser step does not finish the first time.
        </p>
        <div className="mt-4 flex flex-wrap gap-3">
          <button type="button" onClick={() => setConnected(true)} className="btn-primary">
            I connected ChatGPT
          </button>
          <button type="button" className="btn-ghost">
            Try again
          </button>
        </div>
      </div>
      <div className="mt-6 flex justify-between">
        <button onClick={onBack} className="btn-ghost">Back</button>
        <button onClick={onNext} className="btn-primary" disabled={!connected}>
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
        Pairing works like WhatsApp Web. Once paired, WhatsApp becomes the
        easiest way to talk to Wira while the agent runs on this computer.
      </p>
      <ol className="mt-6 space-y-3 text-sm text-ink-muted">
        <li><strong className="text-ink">1.</strong> Open WhatsApp on your phone.</li>
        <li><strong className="text-ink">2.</strong> Go to Linked Devices.</li>
        <li><strong className="text-ink">3.</strong> Tap Link a Device.</li>
        <li><strong className="text-ink">4.</strong> Scan the code Wira shows.</li>
      </ol>
      <div className="mt-6 rounded-xl border border-border bg-canvas p-4 text-sm text-ink-muted">
        When the code is scanned, send Wira a first message like “summarize my day”
        or “find the latest invoice in Downloads.”
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
          <li>• “Summarize my day.”</li>
          <li>• “Find my latest invoice PDF.”</li>
          <li>• “Make a shipping plan for this project.”</li>
          <li>• “Remind me what I was working on.”</li>
        </ul>
        <div className="mt-4 text-xs text-ink-muted">
          Number: {state.phone || "your WhatsApp"} · Safety: {state.safetyMode === "ask" ? "ask first" : "move fast carefully"}
        </div>
      </div>
      <div className="mt-6 flex justify-between">
        <button onClick={onBack} className="btn-ghost">Back</button>
        <a href="/" className="btn-primary">Done</a>
      </div>
    </>
  );
}
