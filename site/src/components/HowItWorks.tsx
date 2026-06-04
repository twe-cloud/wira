const STEPS = [
  {
    n: "01",
    title: "Connect ChatGPT",
    body:
      "Use the ChatGPT subscription you already have. Wira keeps the connection step plain and brings you back into setup when it is done.",
  },
  {
    n: "02",
    title: "Connect WhatsApp",
    body:
      "Scan a QR code from WhatsApp → Linked Devices. Your phone becomes the fastest way to reach the agent on your computer.",
  },
  {
    n: "03",
    title: "Start chatting",
    body:
      "Send your first command from WhatsApp: summarize a day, find a file, make a plan, or check what needs attention.",
  },
];

export default function HowItWorks() {
  return (
    <section id="how" className="container-prose py-20">
      <div className="max-w-2xl">
        <h2 className="text-4xl">A softer path into real agent work.</h2>
        <p className="mt-3 text-ink-muted text-lg">
          Your agent lives on this computer. Wira connects ChatGPT, connects
          WhatsApp, then lets you start from the phone you already use all day.
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
