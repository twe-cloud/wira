import { Link, useSearchParams } from "react-router-dom";
import Footer from "@/components/Footer";
import Nav from "@/components/Nav";
import { PRODUCT } from "@/lib/brand";

export default function Success() {
  const [params] = useSearchParams();
  const sessionId = params.get("session_id");

  return (
    <>
      <Nav />
      <main className="container-narrow py-20 text-center">
        <div className="inline-flex items-center justify-center w-14 h-14 rounded-full bg-accent-soft text-accent text-2xl">
          ✓
        </div>
        <h1 className="mt-6 text-5xl">You're in.</h1>
        <p className="mt-4 text-lg text-ink-muted">
          Welcome to {PRODUCT.name}. Next step: connect your WhatsApp and teach
          it your voice. Takes about five minutes — your assistant is ready to
          take its first message right after.
        </p>

        <div className="mt-8 flex justify-center gap-3 flex-wrap">
          <Link to="/onboarding" className="btn-primary">
            Start onboarding
          </Link>
          <a href={`mailto:${PRODUCT.supportEmail}`} className="btn-ghost">
            Need a hand?
          </a>
        </div>

        {sessionId && (
          <p className="mt-10 text-xs text-ink-muted">
            Receipt reference:{" "}
            <code className="bg-surface border border-border rounded px-1.5 py-0.5">
              {sessionId.slice(0, 12)}…
            </code>{" "}
            (Stripe will email you a copy.)
          </p>
        )}
      </main>
      <Footer />
    </>
  );
}
