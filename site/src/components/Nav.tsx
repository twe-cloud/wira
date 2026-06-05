import { Link } from "react-router-dom";
import { PRODUCT } from "@/lib/brand";

const homePricingHref = `${import.meta.env.BASE_URL}#pricing`;
const homeHowHref = `${import.meta.env.BASE_URL}#how`;
const homePromiseHref = `${import.meta.env.BASE_URL}#promise`;
const logoSrc = `${import.meta.env.BASE_URL}wira-logo.png`;

type NavProps = {
  hideGetStarted?: boolean;
};

export default function Nav({ hideGetStarted = false }: NavProps) {
  return (
    <header className="sticky top-0 z-30 border-b border-border/60 bg-canvas/80 backdrop-blur">
      <div className="container-prose flex h-16 items-center justify-between">
        <Link to="/" className="flex items-center gap-2 font-display text-xl">
          <img
            src={logoSrc}
            alt="Wira logo"
            className="h-7 w-7 rounded-full object-cover"
          />
          <span>{PRODUCT.name}</span>
        </Link>
        <nav className="flex items-center gap-1 text-sm sm:gap-3">
          <a href={homeHowHref} className="hidden px-3 py-2 text-ink-muted hover:text-ink sm:inline">
            How it works
          </a>
          <a href={homePromiseHref} className="hidden px-3 py-2 text-ink-muted hover:text-ink lg:inline">
            Why it matters
          </a>
          <Link to="/learn" className="hidden px-3 py-2 text-ink-muted hover:text-ink sm:inline">
            Learn
          </Link>
          <a href={homePricingHref} className="hidden px-3 py-2 text-ink-muted hover:text-ink sm:inline">
            Pricing
          </a>
          <a href={`${import.meta.env.BASE_URL}#faq`} className="hidden px-3 py-2 text-ink-muted hover:text-ink sm:inline">
            FAQ
          </a>
          {!hideGetStarted && (
            <a href={homePricingHref} className="btn-primary !h-10 !px-4 !text-sm">
              Get started
            </a>
          )}
        </nav>
      </div>
    </header>
  );
}
