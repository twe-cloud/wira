const STEPS = [
  {
    n: "01",
    title: "Connect a brain",
    body:
      "Start with ChatGPT, Claude, GPT, or a local model. Wira handles the setup path so you don't need to learn agent infrastructure first.",
  },
  {
    n: "02",
    title: "Pair WhatsApp",
    body:
      "Scan a QR code from WhatsApp → Linked Devices. Same low-friction move as WhatsApp Web, but now it becomes the doorway into your local agent.",
  },
  {
    n: "03",
    title: "Unlock real work",
    body:
      "Confirm owner lock and safe permissions. Then start issuing real commands from your phone while the actual runtime lives on your computer.",
  },
];

export default function HowItWorks() {
  return (
    <section id="how" className="container-prose py-20">
      <div className="max-w-2xl">
        <h2 className="text-4xl">A softer path into agentic work.</h2>
        <p className="mt-3 text-ink-muted text-lg">
          No need to begin with CLI tabs, profiles, tools, and skills. Wira lets
          you start from your phone, then grow into the deeper Hermes surfaces
          when you're ready.
        </p>
      </div>
      <ol className="mt-12 grid md:grid-cols-3 gap-5">
        {STEPS.map((s) => (
          <li key={s.n} className="card p-7">
            <div className="font-display text-5xl text-accent">{s.n}</div>
            <h3 className="mt-2 text-2xl">{s.title}</h3>
            <p className="mt-3 text-ink-muted">{s.body}</p>
          </li>
        ))}
      </ol>
    </section>
  );
}
