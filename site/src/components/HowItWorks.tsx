const STEPS = [
  {
    n: "01",
    title: "Connect your WhatsApp",
    body:
      "Scan a QR code from WhatsApp → Linked Devices. Same way you'd connect WhatsApp Web. Takes about 60 seconds.",
  },
  {
    n: "02",
    title: "Teach it your voice",
    body:
      "Paste three recent replies you've written. It picks up your phrasing, your emojis, your “lol noted.” Or skip and use a warm default.",
  },
  {
    n: "03",
    title: "Choose who it answers",
    body:
      "By default, it drafts a reply for every message and pings you to approve. Promote contacts to auto-send once you trust it with them.",
  },
];

export default function HowItWorks() {
  return (
    <section id="how" className="container-prose py-20">
      <div className="max-w-2xl">
        <h2 className="text-4xl">Live in five minutes.</h2>
        <p className="mt-3 text-ink-muted text-lg">
          No new app for your contacts. No new number to share. Same WhatsApp
          they already use to reach you.
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
