import { Link, useSearchParams } from "react-router-dom";
import Footer from "@/components/Footer";
import Nav from "@/components/Nav";
import { PRODUCT } from "@/lib/brand";

export default function Success() {
  const [params] = useSearchParams();
  const sessionId = params.get("session_id");
  const publicDownloadUrl =
    typeof window === "undefined"
      ? PRODUCT.downloadMacUrl
      : new URL(PRODUCT.downloadMacUrl, window.location.origin).toString();
  const windowsDownloadUrl =
    typeof window === "undefined"
      ? PRODUCT.downloadWindowsUrl
      : new URL(PRODUCT.downloadWindowsUrl, window.location.origin).toString();

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
                On Mac, drag it to Applications and open it. On Windows, run the
                installer. The setup screen appears automatically.
              </p>
              <div className="mt-2 flex flex-wrap gap-2">
                <a href={publicDownloadUrl} className="btn-primary inline-flex text-sm">
                  Download for Mac
                </a>
                <a href={windowsDownloadUrl} className="btn-ghost inline-flex text-sm">
                  Download for Windows (beta)
                </a>
              </div>
              <p className="mt-1 text-xs text-ink-muted">
                {PRODUCT.systemRequirement}
              </p>
              <p className="mt-1 text-xs text-ink-muted">
                {PRODUCT.windowsBetaNote}
              </p>
            </div>
          </li>
          <li className="flex gap-4">
            <span className="flex-none flex items-center justify-center w-8 h-8 rounded-full bg-accent text-white text-sm font-bold">2</span>
            <div>
              <div className="font-medium">Pick a brain</div>
              <p className="mt-1 text-sm text-ink-muted">
                {PRODUCT.name} asks how it should think. Start free, connect
                your ChatGPT subscription, or keep the brain private when your
                machine is a good fit. You can switch any time.
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
          Save your download links now so you do not lose them if you close this tab:
          <div className="mt-2 text-xs uppercase tracking-wide text-ink-muted">Mac</div>
          <div className="mt-1 break-all rounded-lg border border-border bg-surface px-3 py-2 text-ink">
            {publicDownloadUrl}
          </div>
          <div className="mt-3 text-xs uppercase tracking-wide text-ink-muted">Windows (beta)</div>
          <div className="mt-1 break-all rounded-lg border border-border bg-surface px-3 py-2 text-ink">
            {windowsDownloadUrl}
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
