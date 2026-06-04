# Wira Status

Updated: 2026-06-04
Mode: BUSINESS
Canonical repo: `/Users/motwe/Wira`
Remote: `git@github.com:twe-cloud/wira.git`
Public product page: `https://nibiashara.biz/products/wira/`
Operating surface (live): `https://wira-local-agent.nibiashara.workers.dev` (Cloudflare Workers)

## Current state

Wira is the productized WhatsApp assistant lane for small businesses.

Product closeout pass on 2026-06-04 tightened the public onboarding/site copy around the fastest path to first WhatsApp use. Wira still lives on the buyer's computer and is reached from WhatsApp, but the buyer is now steered toward the fastest free start first, with the ChatGPT-subscription path also kept obvious and easy. The site onboarding flow now follows Welcome → Pick a brain → Connect WhatsApp → Safety → Ready, and the post-payment success page gives a numbered download → brain → QR path instead of dropping the buyer into ambiguity.

Hosting moved off Netlify onto Cloudflare Workers on 2026-06-03. `site/` now serves the built Vite SPA from the Worker's static-assets binding and handles the two Stripe routes (`/api/checkout`, `/api/webhook`) in `site/cloudflare/worker.ts` (Workers-compatible async signature verification). Config in `site/wrangler.jsonc`; security headers in `site/public/_headers`. The Netlify config + functions were removed. Live operating surface: `https://wira-local-agent.nibiashara.workers.dev`.

Stripe is now fully configured on the Worker (2026-06-03). Both `STRIPE_SECRET_KEY` (live standard key "wira-cloudflare-worker") and `STRIPE_WHSEC` are set as Worker secrets (confirmed via `wrangler secret list`). Live webhook destination "Wira Cloudflare Worker" → `/api/webhook` is Active on `checkout.session.completed` (destination `we_1TePjeRVrXHv0YFpqVWS94mG`, account `acct_1SyCfmRVrXHv0YFp`). A live checkout test against price `price_1TcrAXRVrXHv0YFpfmw35hIw` returned a real `cs_live_` Checkout Session (200) — the purchase loop works end to end. Recommended follow-up: rotate the full-access standard key to a restricted key scoped to Checkout Sessions: Write.

Two lanes stay separate:

- **Wira Local** — self-hosted / owner-controlled linked-device assistant for a founder, demo, or low-volume private use.
- **Wira Business** — managed business-number deployment using the official WhatsApp Business Cloud API path, approval policy, monitoring, and Ni Biashara operating support.

## Verified truth as of 2026-05-31

- The Wira codebase includes the WhatsApp Business Cloud API transport in `agent/whatsapp_cloud.py` and webhook server in `agent/cloud_webhook.py`.
- The transport verifies Meta webhook challenge tokens, supports `X-Hub-Signature-256` verification when an app secret is configured, deduplicates inbound message IDs, and routes inbound text into the Wira brain/memory/draft policy.
- The Cloud webhook now forces the `business_cloud` prompt profile. Customer replies speak as the client business via `BUSINESS_NAME` and the WhatsApp Business display name. Wira remains the owner/admin product surface; Hermes remains internal and must not appear in customer-facing chat.
- The customer journey is now documented in `site/docs/customer-journey.md`: Local returns to a setup checklist for installer/brain/QR/onboarding, while Hosted returns to a managed setup checklist for business map, WhatsApp number path, draft-first launch, and smoke checks.
- Wira Local now keeps buyer-owned config, auth, WhatsApp pairing, memory, drafts, and onboarding state under `~/.wira`; the GUI exposes a Check for Updates button that opens the latest GitHub release page. This keeps Local positioned as self-managed enablement after setup, not managed support.
- Tests pass with `python3 -m unittest -q` from `agent/`.
- The code now accepts both Wira-specific `WHATSAPP_CLOUD_*` env names and the shared Ni Biashara Meta credential profile env names from `meta-whatsapp-ni-biashara-cloud-api`:
  - `WHATSAPP_ACCESS_TOKEN`
  - `WHATSAPP_PHONE_NUMBER_ID`
  - `WHATSAPP_WEBHOOK_VERIFY_TOKEN`
  - `WHATSAPP_APP_SECRET`
- The shared Ni Biashara WhatsApp Cloud API profile is available for token/phone/verify-token runtime injection. App-secret hardening must be present before calling a standalone Wira Business deployment fully unattended production-ready.
- Ni Biashara Operator has the live-proven WhatsApp number/runtime path; Wira Business should be sold as a managed per-business deployment using that proven Cloud API pattern, not as a pre-existing standalone hosted Wira instance for every customer.

## Sales-safe wording

Use this language externally:

> Wira can run two ways: a local owner-controlled assistant for small teams, or a managed WhatsApp Business Cloud API deployment for customer-facing use. Ni Biashara already operates the Cloud API path and provisions each business deployment with the right approval policy, monitoring, and handoff rules.

Avoid this language until a specific customer deployment has been provisioned and smoke-tested:

- “Standalone Wira Business hosting is live for all customers.”
- “Fully unattended WhatsApp replies are production-ready.”
- “No owner review needed.”

## Product-direction reset

The current repo still reflects an older draft/reply assistant thesis in runtime, docs, and site copy. The active founder direction is different:

- **Wira Local** should be a branded WhatsApp command surface for a real local Hermes agent living on the buyer's computer.
- **Wira Business** should also be owner/operator-first: a branded command surface for a solo operator, not a default customer auto-reply or ops-assistant product.
- Keep **Wira** as both the product name and the local agent name until the user naturally discovers Hermes.
- Hermes CLI/Desktop discovery should happen organically after onboarding rather than being the scary first step.

Source-of-truth re-architecture plan:
- `docs/plans/2026-06-03-wira-hermes-command-surface.md`

## Next production closeout

1. Finish the actual runtime bridge hardening so owner WhatsApp commands run through the real Wira/Hermes profile path with durable session/state receipts.
2. Replace any remaining advanced/admin docs that still describe legacy responder setup as the primary Local flow.
3. Rework the WhatsApp local transport so owner-issued messages become the primary command path.
4. Bridge Wira into a real Hermes runtime/profile instead of the current single-prompt reply generator.
5. Only then re-evaluate whether any responder/draft workflows remain worth keeping as an optional later mode.
