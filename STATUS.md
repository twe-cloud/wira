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

## Next production closeout

1. Add or confirm `WHATSAPP_APP_SECRET` in the governed Meta WhatsApp credential profile or each deployment’s secret store.
2. Start Wira Business in draft-first mode for the first customer deployment.
3. Run one real Meta webhook challenge verification, one signed inbound message test, one draft creation test, and one owner-approved outbound send.
4. Only then label that specific customer deployment as live unattended-capable.
