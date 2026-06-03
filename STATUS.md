# Wira Status

Updated: 2026-06-01
Mode: BUSINESS
Canonical repo: `/Users/motwe/Wira`
Remote: `git@github.com:twe-cloud/wira.git`
Public product page: `https://nibiashara.biz/products/wira/`

## Current state

Wira is the productized WhatsApp assistant lane for small businesses.

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
- Default local agent name should be **Vera**, with rename available after setup.
- Hermes CLI/Desktop discovery should happen organically after onboarding rather than being the scary first step.

Source-of-truth re-architecture plan:
- `docs/plans/2026-06-03-wira-hermes-command-surface.md`

## Next production closeout

1. Rewrite product/site/runtime copy so Wira is positioned as a branded Hermes command surface, not a drafting bot.
2. Replace Local onboarding steps centered on voice samples/reply mode with owner-lock, permissions, and Hermes-runtime setup.
3. Rework the WhatsApp local transport so owner-issued messages become the primary command path.
4. Bridge Wira into a real Hermes runtime/profile instead of the current single-prompt reply generator.
5. Only then re-evaluate whether any responder/draft workflows remain worth keeping as an optional later mode.
