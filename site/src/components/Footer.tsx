import { Link } from "react-router-dom";
import { PRODUCT } from "@/lib/brand";

const homeHowHref = `${import.meta.env.BASE_URL}#how`;
const homePromiseHref = `${import.meta.env.BASE_URL}#promise`;
const homePricingHref = `${import.meta.env.BASE_URL}#pricing`;
const homeFaqHref = `${import.meta.env.BASE_URL}#faq`;

export default function Footer() {
  const year = new Date().getFullYear();
  return (
    <footer className="mt-24 border-t border-border py-12 text-sm text-ink-muted">
      <div className="container-prose grid grid-cols-2 gap-8 sm:grid-cols-4">
        <div className="col-span-2">
          <div className="font-display text-xl text-ink">{PRODUCT.name}</div>
          <p className="mt-2 max-w-xs">{PRODUCT.description}</p>
        </div>
        <div>
          <div className="mb-3 font-medium text-ink">Product</div>
          <ul className="space-y-2">
            <li><a href={homeHowHref} className="hover:text-ink">How it works</a></li>
            <li><a href={homePromiseHref} className="hover:text-ink">Why it matters</a></li>
            <li><a href={homePricingHref} className="hover:text-ink">Pricing</a></li>
            <li><a href={homeFaqHref} className="hover:text-ink">FAQ</a></li>
            <li><Link to="/learn" className="hover:text-ink">Learn</Link></li>
          </ul>
        </div>
        <div>
          <div className="mb-3 font-medium text-ink">Company</div>
          <ul className="space-y-2">
            <li><Link to="/nerd-stuff" className="hover:text-ink">Nerd stuff</Link></li>
            <li><Link to="/privacy" className="hover:text-ink">Privacy</Link></li>
            <li><Link to="/terms" className="hover:text-ink">Terms</Link></li>
            <li><a href={`mailto:${PRODUCT.supportEmail}`} className="hover:text-ink">Contact</a></li>
          </ul>
        </div>
      </div>
      <div className="container-prose mt-10 text-xs">
        {PRODUCT.legalEntity} · Made in {PRODUCT.city} · © {year} {PRODUCT.name}
      </div>
    </footer>
  );
}
