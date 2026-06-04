const STEPS = [
  {
    n: "01",
    title: "Download Wira",
    body:
      "Download the Mac app, drag it to Applications, and open it. Wira lives on your computer — not in a browser tab.",
  },
  {
    n: "02",
    title: "Pick your brain",
    body:
      "Start free in seconds with Groq or DeepSeek, connect the ChatGPT subscription you already have, or use a private local brain on your Mac.",
  },
  {
    n: "03",
    title: "Connect WhatsApp",
    body:
      "Scan the QR code from WhatsApp → Settings → Linked Devices, then send your first command from your phone.",
  },
];

export default function HowItWorks() {
  return (
    <section id="how" className="container-prose py-20">
      <div className="max-w-2xl">
        <h2 className="text-4xl">A softer path into real agent work.</h2>
        <p className="mt-3 text-ink-muted text-lg">
          Your agent lives on this computer. Wira connects a brain, connects
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
