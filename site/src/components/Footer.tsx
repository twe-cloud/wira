import { Link } from "react-router-dom";
import { PRODUCT } from "@/lib/brand";

export default function Footer() {
  const year = new Date().getFullYear();
  return (
    <footer className="border-t border-border mt-24 py-12 text-sm text-ink-muted">
      <div className="container-prose grid grid-cols-2 sm:grid-cols-4 gap-8">
        <div className="col-span-2">
          <div className="font-display text-xl text-ink">{PRODUCT.name}</div>
          <p className="mt-2 max-w-xs">{PRODUCT.description}</p>
        </div>
        <div>
          <div className="font-medium text-ink mb-3">Product</div>
          <ul className="space-y-2">
            <li><a href="/#how" className="hover:text-ink">How it works</a></li>
            <li><a href="/#pricing" className="hover:text-ink">Pricing</a></li>
            <li><a href="/#faq" className="hover:text-ink">FAQ</a></li>
          </ul>
        </div>
        <div>
          <div className="font-medium text-ink mb-3">Company</div>
          <ul className="space-y-2">
            <li><Link to="/privacy" className="hover:text-ink">Privacy</Link></li>
            <li><Link to="/terms" className="hover:text-ink">Terms</Link></li>
            <li><a href={`mailto:${PRODUCT.supportEmail}`} className="hover:text-ink">Contact</a></li>
          </ul>
        </div>
      </div>
      <div className="container-prose mt-10 text-xs">
        Made by humans in {PRODUCT.city} · © {year} {PRODUCT.name}
      </div>
    </footer>
  );
}
