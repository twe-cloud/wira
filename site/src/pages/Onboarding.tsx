import { AnimatePresence, motion } from "motion/react";
import { useEffect, useState } from "react";
import Footer from "@/components/Footer";
import Nav from "@/components/Nav";
import { PRODUCT } from "@/lib/brand";

type State = {
  step: number;
  voiceSamples: string;
  contactPolicy: "whitelist" | "all-except" | "everyone";
  approvalMode: "draft" | "auto-trusted" | "auto-all";
  phone: string;
};

const STORAGE_KEY = "onboarding.v1";

const EMPTY: State = {
  step: 1,
  voiceSamples: "",
  contactPolicy: "whitelist",
  approvalMode: "draft",
  phone: "",
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

const STEPS = ["Connect", "Voice", "Contacts", "Approval", "First reply"];

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
        <div className="flex items-center gap-2 mb-8" aria-label="Progress">
          {STEPS.map((label, i) => {
            const n = i + 1;
            const done = n < state.step;
            const active = n === state.step;
            return (
              <div key={label} className="flex-1 flex items-center gap-2">
                <div
                  className={`flex-1 h-1.5 rounded-full ${
                    done || active ? "bg-accent" : "bg-border"
                  }`}
                />
              </div>
            );
          })}
        </div>
        <p className="text-sm text-ink-muted mb-2">
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
            {state.step === 1 && (
              <Step1Connect
                phone={state.phone}
                setPhone={(v) => set("phone", v)}
                onNext={next}
              />
            )}
            {state.step === 2 && (
              <Step2Voice
                samples={state.voiceSamples}
                setSamples={(v) => set("voiceSamples", v)}
                onNext={next}
                onBack={back}
              />
            )}
            {state.step === 3 && (
              <Step3Contacts
                value={state.contactPolicy}
                setValue={(v) => set("contactPolicy", v)}
                onNext={next}
                onBack={back}
              />
            )}
            {state.step === 4 && (
              <Step4Approval
                value={state.approvalMode}
                setValue={(v) => set("approvalMode", v)}
                onNext={next}
                onBack={back}
              />
            )}
            {state.step === 5 && <Step5Done state={state} onBack={back} />}
          </motion.div>
        </AnimatePresence>

        <p className="mt-6 text-xs text-ink-muted text-center">
          Your answers are saved locally as you go. Nothing's submitted until
          you click finish.
        </p>
      </main>
      <Footer />
    </>
  );
}

function Step1Connect({
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
      <h2 className="text-3xl">Connect your WhatsApp</h2>
      <p className="mt-2 text-ink-muted">
        Enter the WhatsApp number {PRODUCT.name} will live on. We'll send you a
        magic link to scan the QR code from your phone.
      </p>
      <label className="block mt-6 text-sm font-medium">WhatsApp number</label>
      <input
        type="tel"
        inputMode="tel"
        autoComplete="tel"
        placeholder="+254 700 000 000"
        value={phone}
        onChange={(e) => setPhone(e.target.value)}
        className="mt-2 w-full bg-canvas border border-border rounded-xl px-4 py-3 text-base focus:outline-none"
      />
      <p className="mt-2 text-xs text-ink-muted">
        Include the country code. We never message this number — only use it to
        link your assistant.
      </p>
      <div className="mt-6 flex justify-end">
        <button
          disabled={!phone.trim()}
          onClick={onNext}
          className="btn-primary disabled:opacity-40"
        >
          Send me the link →
        </button>
      </div>
    </>
  );
}

function Step2Voice({
  samples,
  setSamples,
  onNext,
  onBack,
}: {
  samples: string;
  setSamples: (v: string) => void;
  onNext: () => void;
  onBack: () => void;
}) {
  return (
    <>
      <h2 className="text-3xl">Teach it your voice</h2>
      <p className="mt-2 text-ink-muted">
        Paste 3-5 recent replies you've sent on WhatsApp. {PRODUCT.name} will
        mirror your phrasing, emojis, and pacing. You can update this later.
      </p>
      <textarea
        value={samples}
        onChange={(e) => setSamples(e.target.value)}
        rows={8}
        placeholder={"e.g.\n\nsure, sending now 🤝\nhaha yes lemme check\nWill loop back tomorrow AM, sound good?"}
        className="mt-6 w-full bg-canvas border border-border rounded-xl px-4 py-3 text-base focus:outline-none font-mono"
      />
      <div className="mt-6 flex justify-between">
        <button onClick={onBack} className="btn-ghost">
          Back
        </button>
        <button onClick={onNext} className="btn-primary">
          {samples.trim() ? "Continue →" : "Skip — use default warm tone"}
        </button>
      </div>
    </>
  );
}

function Step3Contacts({
  value,
  setValue,
  onNext,
  onBack,
}: {
  value: State["contactPolicy"];
  setValue: (v: State["contactPolicy"]) => void;
  onNext: () => void;
  onBack: () => void;
}) {
  const options: { id: State["contactPolicy"]; title: string; body: string }[] = [
    {
      id: "whitelist",
      title: "Only specific contacts (recommended)",
      body: "Pick who can get replies. Safest start — promote contacts as you build trust.",
    },
    {
      id: "all-except",
      title: "Everyone except a blocklist",
      body: "Replies to all incoming DMs except contacts you explicitly exclude.",
    },
    {
      id: "everyone",
      title: "Everyone who DMs you",
      body: "Maximum coverage. Best for high-volume operators who triage later.",
    },
  ];

  return (
    <>
      <h2 className="text-3xl">Who can it answer?</h2>
      <p className="mt-2 text-ink-muted">
        Group chats are off by default. You can change this any time.
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
              name="policy"
              checked={value === o.id}
              onChange={() => setValue(o.id)}
              className="sr-only"
            />
            <div className="font-medium">{o.title}</div>
            <div className="text-sm text-ink-muted mt-1">{o.body}</div>
          </label>
        ))}
      </div>
      <div className="mt-6 flex justify-between">
        <button onClick={onBack} className="btn-ghost">
          Back
        </button>
        <button onClick={onNext} className="btn-primary">
          Continue →
        </button>
      </div>
    </>
  );
}

function Step4Approval({
  value,
  setValue,
  onNext,
  onBack,
}: {
  value: State["approvalMode"];
  setValue: (v: State["approvalMode"]) => void;
  onNext: () => void;
  onBack: () => void;
}) {
  const options: { id: State["approvalMode"]; title: string; body: string }[] = [
    {
      id: "draft",
      title: "Always draft, ask me to send",
      body: "Safest. You approve every reply with one tap. Recommended for week one.",
    },
    {
      id: "auto-trusted",
      title: "Auto-send for trusted contacts, draft for everyone else",
      body: "Best of both. Promote contacts to trusted as you build confidence.",
    },
    {
      id: "auto-all",
      title: "Auto-send for everyone",
      body: "Hands-free. We still escalate edge cases to you.",
    },
  ];

  return (
    <>
      <h2 className="text-3xl">How much trust to start with?</h2>
      <p className="mt-2 text-ink-muted">
        You can change this mid-conversation. Every reply has an edit button.
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
              name="approval"
              checked={value === o.id}
              onChange={() => setValue(o.id)}
              className="sr-only"
            />
            <div className="font-medium">{o.title}</div>
            <div className="text-sm text-ink-muted mt-1">{o.body}</div>
          </label>
        ))}
      </div>
      <div className="mt-6 flex justify-between">
        <button onClick={onBack} className="btn-ghost">
          Back
        </button>
        <button onClick={onNext} className="btn-primary">
          Continue →
        </button>
      </div>
    </>
  );
}

function Step5Done({ state, onBack }: { state: State; onBack: () => void }) {
  return (
    <>
      <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-accent-soft text-accent text-xl">
        ✓
      </div>
      <h2 className="mt-4 text-3xl">You're set.</h2>
      <p className="mt-2 text-ink-muted">
        We've emailed a one-time link to activate {PRODUCT.name} on{" "}
        <span className="text-ink font-medium">{state.phone || "your number"}</span>.
        Open it from your phone to scan the QR — that's the final step.
      </p>
      <div className="mt-6 bg-canvas border border-border rounded-xl p-4 text-sm">
        <div className="font-medium mb-2">Your settings</div>
        <ul className="text-ink-muted space-y-1">
          <li>Voice: {state.voiceSamples.trim() ? "trained from samples" : "default warm tone"}</li>
          <li>Contacts: {state.contactPolicy}</li>
          <li>Approval: {state.approvalMode}</li>
        </ul>
      </div>
      <div className="mt-6 flex justify-between">
        <button onClick={onBack} className="btn-ghost">
          Back
        </button>
        <a href="/" className="btn-primary">
          Done
        </a>
      </div>
    </>
  );
}
