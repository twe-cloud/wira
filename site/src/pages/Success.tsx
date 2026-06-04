import { Link, useSearchParams } from "react-router-dom";
import Footer from "@/components/Footer";
import Nav from "@/components/Nav";
import { PRODUCT } from "@/lib/brand";

export default function Success() {
  const [params] = useSearchParams();
  const sessionId = params.get("session_id");

  return (
    <>
      <Nav hideGetStarted />
      <main className="container-narrow py-20">
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-full bg-accent-soft text-accent text-2xl">
            ✓
          </div>
          <h1 className="mt-6 text-5xl">You're in.</h1>
          <p className="mt-4 text-lg text-ink-muted">
            Welcome to {PRODUCT.name}. Three short steps and your agent is live
            on WhatsApp.
          </p>
        </div>

        <ol className="mt-10 space-y-5 text-left max-w-md mx-auto">
          <li className="flex gap-4">
            <span className="flex-none flex items-center justify-center w-8 h-8 rounded-full bg-accent text-white text-sm font-bold">1</span>
            <div>
              <div className="font-medium">Download &amp; open {PRODUCT.name}</div>
              <p className="mt-1 text-sm text-ink-muted">
                Drag it to Applications, then open it. The setup screen appears automatically.
              </p>
              <a href={PRODUCT.downloadMacUrl} className="btn-primary mt-2 inline-flex text-sm">
                Download for Mac
              </a>
              <p className="mt-1 text-xs text-ink-muted">
                {PRODUCT.systemRequirement}
              </p>
            </div>
          </li>
          <li className="flex gap-4">
            <span className="flex-none flex items-center justify-center w-8 h-8 rounded-full bg-accent text-white text-sm font-bold">2</span>
            <div>
              <div className="font-medium">Pick a brain</div>
              <p className="mt-1 text-sm text-ink-muted">
                {PRODUCT.name} asks how it should think. Start free, connect
                your ChatGPT subscription, or keep it fully private on your
                Mac. You can switch any time.
              </p>
            </div>
          </li>
          <li className="flex gap-4">
            <span className="flex-none flex items-center justify-center w-8 h-8 rounded-full bg-accent text-white text-sm font-bold">3</span>
            <div>
              <div className="font-medium">Scan the WhatsApp QR</div>
              <p className="mt-1 text-sm text-ink-muted">
                Open WhatsApp on your phone, go to Linked Devices, and scan the
                code {PRODUCT.name} shows. Send your first message — done.
              </p>
            </div>
          </li>
        </ol>

        <div className="mt-10 text-center">
          <Link to="/onboarding" className="btn-ghost">
            Need the full walkthrough? Start guided setup
          </Link>
        </div>

        <div className="mt-6 rounded-xl border border-border bg-canvas p-4 text-sm text-ink-muted max-w-xl mx-auto">
          Save this download link now so you do not lose it if you close this tab:
          <div className="mt-2 break-all rounded-lg border border-border bg-surface px-3 py-2 text-ink">
            {PRODUCT.downloadMacUrl}
          </div>
        </div>

        <div className="mt-6 text-center text-xs text-ink-muted">
          <p>
            Need a hand?{" "}
            <a href={`mailto:${PRODUCT.supportEmail}`} className="underline">
              {PRODUCT.supportEmail}
            </a>
          </p>
        </div>

        {sessionId && (
          <p className="mt-10 text-center text-xs text-ink-muted">
            Receipt reference:{" "}
            <code className="bg-surface border border-border rounded px-1.5 py-0.5">
              {sessionId.slice(0, 12)}…
            </code>{" "}
            (Stripe emails the receipt. Save the download link above.)
          </p>
        )}
      </main>
      <Footer />
    </>
  );
}
