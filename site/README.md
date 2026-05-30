# Marketing + onboarding site

The customer-facing site for the WhatsApp AI assistant product. Vite + React 19 + Tailwind 4 + Motion. Deploys to Netlify. Stripe Checkout for payments.

Designed to be drop-in portable to the main business site (vita) — same stack, same conventions.

## Run locally

```bash
npm install
cp .env.example .env       # fill in your Stripe test keys
npm run dev                 # site only, no Stripe Functions
npm run netlify:dev         # site + Stripe Functions (needs netlify CLI)
```

Open http://localhost:3001.

## Build

```bash
npm run build        # typecheck + production build → ./dist
npm run preview      # serve the built site locally
```

## Deploy to Netlify

```bash
# one-time
npm install -g netlify-cli
netlify login
netlify init         # link this folder to a Netlify site

# every deploy
npm run netlify:deploy            # preview deploy
npm run netlify:deploy:prod        # production
```

Set these env vars in **Netlify dashboard → Site settings → Environment variables**:

| Variable | Where to get it |
|---|---|
| `STRIPE_SECRET_KEY` | Stripe dashboard → Developers → API keys (`sk_test_*` or `sk_live_*`) |
| `STRIPE_WHSEC` | Stripe dashboard → Developers → Webhooks → add endpoint → `https://your-site.netlify.app/.netlify/functions/webhook` → reveal signing secret |
| `SITE_URL` | Your public URL, e.g. `https://your-site.netlify.app`. Used for Stripe redirects. |

Then in `src/lib/brand.ts` paste your Stripe **Price IDs** (`price_*`) for the monthly and annual plans.

## Layout

```
src/
  pages/           Home, Success, Onboarding, Privacy, Terms, NotFound
  components/      Hero, PhoneMockup, Pillars, HowItWorks, VoiceToggle,
                   Pricing, FAQ, Nav, Footer, SocialProof
  lib/
    brand.ts       Product name, copy, pricing — single source of truth
    stripe.ts      Client-side bridge to checkout function

netlify/functions/
  checkout.ts      Creates a Stripe Checkout Session
  webhook.ts       Verifies + handles Stripe events

docs/              Customer-facing markdown docs
public/            favicon, robots, sitemap
```

## Renaming the product

Everything customer-facing reads from `src/lib/brand.ts`. Change `PRODUCT.name`, `PRODUCT.domain`, etc. there and the whole site updates.

The repo folder is currently `site/` — rename to whatever once the final name is locked.

## Testing the Stripe loop end to end

1. In Stripe dashboard, create test-mode Products with monthly + annual Prices.
2. Paste the Price IDs into `src/lib/brand.ts`.
3. Run `npm run netlify:dev`.
4. Click **Get started**. Stripe Checkout opens with test card prefilled — use `4242 4242 4242 4242`, any future expiry, any CVC.
5. After "payment", you land on `/success?session_id=cs_test_...`.
6. To test the webhook: `stripe listen --forward-to localhost:8888/.netlify/functions/webhook` then trigger an event with `stripe trigger checkout.session.completed`.

## Porting to the main business site

Two ways:

- **Subpath** (recommended) — host this build under `/[product]` on the main site. Update `base` in `vite.config.ts` and the `<Routes>` paths accordingly.
- **Subdomain** — host as-is at `[product].yourdomain.com`. Easier; better for marketing analytics separation.

The `src/components` folder is designed to be lifted into the main app's component tree as a single feature module.
