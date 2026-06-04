import { Link } from "react-router-dom";
import { PRODUCT } from "@/lib/brand";

export default function Nav() {
  return (
    <header className="sticky top-0 z-30 backdrop-blur bg-canvas/80 border-b border-border/60">
      <div className="container-prose flex h-16 items-center justify-between">
        <Link to="/" className="flex items-center gap-2 font-display text-xl">
          <span
            aria-hidden
            className="inline-block w-6 h-6 rounded-full bg-accent"
            style={{ boxShadow: "inset -2px -2px 0 rgba(0,0,0,.06)" }}
          />
          <span>{PRODUCT.name}</span>
        </Link>
        <nav className="flex items-center gap-1 sm:gap-3 text-sm">
          <a href="#how" className="hidden sm:inline px-3 py-2 text-ink-muted hover:text-ink">
            How it works
          </a>
          <Link to="/learn" className="hidden sm:inline px-3 py-2 text-ink-muted hover:text-ink">
            Learn
          </Link>
          <a href="#pricing" className="hidden sm:inline px-3 py-2 text-ink-muted hover:text-ink">
            Pricing
          </a>
          <a href="#faq" className="hidden sm:inline px-3 py-2 text-ink-muted hover:text-ink">
            FAQ
          </a>
          <a href="#pricing" className="btn-primary !h-10 !px-4 !text-sm">
            Get started
          </a>
        </nav>
      </div>
    </header>
  );
}
