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

const STEPS = ["Connect", "Brain", "Permissions", "Safety", "Pairing"];

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
          This preview flow is being realigned around the branded-Hermes thesis.
          The important promise is a local agent you can grow with — not a draft
          bot disguised as one.
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
      <h2 className="text-3xl">Choose where your agent will live</h2>
      <p className="mt-2 text-ink-muted">
        Enter the WhatsApp number you will use to reach {PRODUCT.name}. This is
        the control surface, not the whole product — the real runtime should
        live on your computer.
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
        Include the country code. This number is how you reach your agent after
        pairing.
      </p>
      <div className="mt-6 flex justify-end">
        <button
          disabled={!phone.trim()}
          onClick={onNext}
          className="btn-primary disabled:opacity-40"
        >
          Continue →
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
      <h2 className="text-3xl">Connect a brain</h2>
      <p className="mt-2 text-ink-muted">
        This screen is still using older preview fields underneath, but the
        product direction is now clear: the setup should connect a real brain
        and local runtime, not teach a texting persona. For now, think of this
        as the placeholder step where your model/provider path gets wired in.
      </p>
      <textarea
        value={samples}
        onChange={(e) => setSamples(e.target.value)}
        rows={8}
        placeholder={"Temporary preview field.\n\nFinal flow should connect ChatGPT, Claude, GPT, or a local model here."}
        className="mt-6 w-full bg-canvas border border-border rounded-xl px-4 py-3 text-base focus:outline-none font-mono"
      />
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
      title: "Tight access (recommended)",
      body: "This placeholder maps closest to the future owner-lock + narrow-permissions setup.",
    },
    {
      id: "all-except",
      title: "Wider access with exceptions",
      body: "Useful only as a future advanced mode. The default product should remain owner-first and private.",
    },
    {
      id: "everyone",
      title: "Open surface",
      body: "Not the intended Local default. Public access should stay out of the main product thesis.",
    },
  ];

  return (
    <>
      <h2 className="text-3xl">Set access boundaries</h2>
      <p className="mt-2 text-ink-muted">
        The real product needs owner lock plus deliberate access boundaries for
        files, tools, browser, and terminal. This preview still shows the older
        choice structure, but the meaning has changed.
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
      title: "Most cautious",
      body: "Closest to the future permission-first posture: safer defaults before deeper autonomy is unlocked.",
    },
    {
      id: "auto-trusted",
      title: "Balanced trust",
      body: "Represents a later mode where the agent can do more once the owner is confident in it.",
    },
    {
      id: "auto-all",
      title: "Advanced autonomy",
      body: "Should only come after the real Hermes runtime, owner lock, and permission controls are working clearly.",
    },
  ];

  return (
    <>
      <h2 className="text-3xl">Choose a safe starting posture</h2>
      <p className="mt-2 text-ink-muted">
        The long-term product should talk about permissions and autonomy, not
        draft replies. This preview step is being repurposed in that direction.
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
        The intended finish line is simple: pair WhatsApp, start with Vera, and
        send your first real command into a local agent that can later open into
        Hermes Desktop and CLI.
      </p>
      <div className="mt-6 bg-canvas border border-border rounded-xl p-4 text-sm">
        <div className="font-medium mb-2">Current preview summary</div>
        <ul className="text-ink-muted space-y-1">
          <li>Control surface: {state.phone || "your WhatsApp"}</li>
          <li>Brain step placeholder: {state.voiceSamples.trim() ? "configured in preview" : "still to be wired"}</li>
          <li>Access posture: {state.contactPolicy}</li>
          <li>Safety posture: {state.approvalMode}</li>
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
