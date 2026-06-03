# Operator Runbook

The "how to actually run this" doc. Read once end-to-end before launch, then keep open for ops.

This runbook now assumes the corrected product thesis:
- Wira is a branded command surface for a real local Hermes agent
- the primary user is the owner/operator
- WhatsApp is the easiest control surface into that agent
- customer-facing reply automation is not the default product promise

---

## One-time launch checklist

### 1. Stripe
1. Create a Stripe account (test mode is fine for the first week).
2. Create the Wira product/prices.
3. Copy the two **Price IDs** (`price_*`) into `site/src/lib/brand.ts`.
4. Set `STRIPE_SECRET_KEY` and `STRIPE_WHSEC` in Netlify.

### 2. Netlify
```bash
cd site
npm install -g netlify-cli
netlify login
netlify init
netlify env:set STRIPE_SECRET_KEY sk_test_...
netlify env:set STRIPE_WHSEC whsec_...
netlify env:set SITE_URL https://<your-netlify-site>.netlify.app
npm run netlify:deploy:prod
```

### 3. Local runtime truth
Before selling the local product, make sure the product can honestly claim:
- the agent runs on the buyer's computer
- WhatsApp pairing works reliably
- owner-issued messages reach the local runtime
- at least one real tool-backed task can be executed and reported back

### 4. Packaging trust
For macOS distribution, local downloads should be Developer ID signed and notarized before broad paid traffic. Gatekeeper rejection will kill conversion.

---

## New-customer provisioning (current direction)

Until the app is fully self-serve, the operator may still need to help buyers through the first run.

Target flow per new customer:
1. Buyer completes checkout.
2. Buyer downloads Wira.
3. Buyer connects a brain.
4. Buyer pairs WhatsApp.
5. Buyer confirms owner lock and safe permissions.
6. Buyer sends the first real command to Wira.

What you are looking for is not "first reply looks good."
What you are looking for is:
- first command reaches the agent
- first tool-backed task succeeds
- the buyer understands that the agent lives on their computer

---

## Ops checks

### Must verify
- local runtime boots cleanly
- app stays alive after onboarding
- reconnect path works
- WhatsApp owner-lock behavior works
- at least one real command executes successfully
- the product surface still accurately describes what the runtime can do

### Common issues
- **App exits after launch** → local persistence/runtime bug; fix before scaling traffic
- **QR/session expiry** → reconnect flow must be obvious and fast
- **User expects agentic work but gets only drafted text** → thesis mismatch; treat as P0 product issue
- **Copy promises more than runtime can do** → fix copy or runtime immediately; do not let marketing drift ahead of truth

---

## What's not the core thesis anymore
These are no longer the center of gravity:
- sounding exactly like the owner's texting style
- approving drafted replies in a dashboard
- whitelisting contacts for auto-send
- customer support bot positioning

If any of these survive, they should be optional later extensions — not the main onboarding or sales story.

---

## Implementation priority
1. Rewrite all product/site/runtime copy around the branded Hermes thesis
2. Replace onboarding centered on voice/reply mode with owner lock + permissions + runtime setup
3. Rework WhatsApp transport into an owner-command surface
4. Bridge Wira into a real Hermes runtime/profile
5. Only later decide whether responder workflows deserve a separate extension mode
