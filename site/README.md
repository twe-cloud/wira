# Marketing + onboarding site

The customer-facing site for Wira: a branded path into a real local Hermes agent that lives on the buyer's computer and is reached from WhatsApp. Vite + React 19 + Tailwind 4 + Motion. Runs on Cloudflare Workers (static assets + a Worker for the Stripe API routes). Stripe Checkout for payments.

Designed to be drop-in portable to the main business site (vita) — same stack, same conventions.

## Run locally

```bash
npm install
cp .dev.vars.example .dev.vars   # fill in your Stripe test keys (Worker secrets)
npm run dev                       # site only (Vite), no Stripe API
npm run cf:dev                    # site + Stripe API via the Worker (wrangler)
```

`npm run dev` serves the SPA at http://localhost:3001. `npm run cf:dev` serves
the SPA + `/api/*` Worker routes at http://localhost:8787.

## Build

```bash
npm run build        # typecheck + production build → ./dist
npm run preview      # serve the built site locally
```

## Deploy to Cloudflare

```bash
# one-time: set the server secrets (you will be prompted for each value)
npx wrangler secret put STRIPE_SECRET_KEY
npx wrangler secret put STRIPE_WHSEC

# every deploy (builds the SPA, then publishes the Worker + assets)
npm run deploy
```

Config lives in `wrangler.jsonc`. `SITE_URL` (used for Stripe redirects) is a
`[vars]` entry there — update it to the production URL/custom domain.

The buyer-facing Mac download should point at the Worker-owned route
`/download/wira-mac`, not directly at a raw GitHub release URL. That keeps the
public link stable, lets the Worker cache the DMG at the edge, and gives ops a
single surface to update if the release origin changes.

| Value | Where to get it | How it's set |
|---|---|---|
| `STRIPE_SECRET_KEY` | Stripe dashboard → Developers → API keys (`sk_test_*` / `sk_live_*`) | `wrangler secret put` |
| `STRIPE_WHSEC` | Stripe dashboard → Developers → Webhooks → add endpoint `https://<your-worker-url>/api/webhook` → signing secret | `wrangler secret put` |
| `SITE_URL` | Your public URL, e.g. `https://wira-local-agent.workers.dev` or a custom domain | `vars` in `wrangler.jsonc` |

Then in `src/lib/brand.ts` paste the Stripe **Price ID** (`price_*`) for the Wira Local one-time purchase.

## Layout

```
src/
  pages/           Home, Success, Onboarding, Privacy, Terms, NotFound
  components/      Hero, PhoneMockup, Pillars, HowItWorks, VoiceToggle,
                   Pricing, FAQ, Nav, Footer, SocialProof
  lib/
    brand.ts       Product name, copy, pricing — single source of truth
    stripe.ts      Client-side bridge to checkout function

cloudflare/
  worker.ts        Serves the SPA (ASSETS) + /api/checkout + /api/webhook (Stripe)

wrangler.jsonc     Cloudflare Worker config (assets, vars, compat)
docs/              Customer-facing markdown docs
public/            favicon, robots, sitemap, _headers (security headers)
```

## Renaming the product

Everything customer-facing reads from `src/lib/brand.ts`. Change `PRODUCT.name`, `PRODUCT.domain`, etc. there and the whole site updates.

The repo folder is currently `site/` — rename to whatever once the final name is locked.

## Testing the Stripe loop end to end

1. In Stripe dashboard, create a test-mode Product with a one-time Wira Local Price.
2. Paste the Price ID into `src/lib/brand.ts`.
3. Run `npm run cf:dev`.
4. Click **Get started**. Stripe Checkout opens with test card prefilled — use `4242 4242 4242 4242`, any future expiry, any CVC.
5. After "payment", you land on `/success?session_id=cs_test_...`.
6. To test the webhook locally, run `npm run cf:dev`, then forward Stripe to `http://localhost:8787/api/webhook` with `stripe listen --forward-to http://localhost:8787/api/webhook`, then trigger an event with `stripe trigger checkout.session.completed`.

## Porting to the main business site

Two ways:

- **Subpath** (recommended) — host this build under `/[product]` on the main site. Update `base` in `vite.config.ts` and the `<Routes>` paths accordingly.
- **Subdomain** — host as-is at `[product].yourdomain.com`. Easier; better for marketing analytics separation.

The `src/components` folder is designed to be lifted into the main app's component tree as a single feature module.
