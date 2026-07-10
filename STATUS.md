# Wira Status

Updated: 2026-07-09
Mode: BUSINESS
Canonical repo: `/Users/motwe/Wira`
Remote: `git@github.com:twe-cloud/wira.git`
Public product page: `https://nibiashara.biz/products/wira/`
Operating surface (live): `https://wira-local-agent.nibiashara.workers.dev` (Cloudflare Workers)

## Current state

Wira is the productized WhatsApp assistant lane for small businesses.

### 2026-07-09 — Windows signing status correction

Windows signing is **not fully ready yet**, but the Azure infrastructure has been
recreated after the previous account deletion. The GitHub workflow is still wired
for Azure Trusted/Artifact Signing, and the repo has the Azure tenant/client
secrets plus endpoint/account variables.

- Current Azure subscription: `Azure subscription 1`
  (`dccc9905-e9da-4e3a-94d8-a38834814129`), tenant
  `bd301f01-e9a9-4654-979c-d78cf067e750`.
- `Microsoft.CodeSigning` is registered.
- Azure activity log shows `twe-azure-automation` previously deleted
  `Microsoft.CodeSigning/codeSigningAccounts/wirawintrustsign` on
  2026-06-28, including the account-scoped signing role assignments.
- Recreated Artifact Signing account `wirawintrustsign` in
  `wira-win-qa-rg-centralus` on 2026-07-09. Provisioning state: `Succeeded`;
  account URI: `https://cus.codesigning.azure.net/`; SKU: `Basic`.
- Reattached account-scoped roles:
  - `Artifact Signing Identity Verifier` to `twe@nibiashara.biz`
    (`7ddee820-5520-463b-b34a-8b20324d5038`).
  - `Artifact Signing Certificate Profile Signer` to `twe-azure-automation`
    (`f80a454f-62e6-41eb-bba2-65d0bd107407`).
  - `Artifact Signing Identity Verifier` to `twe-azure-automation` as a CLI
    read/probe fallback, though Microsoft still gates validation management to
    the portal.
- Updated GitHub repo secrets on `twe-cloud/wira` so the signing workflow uses
  `twe-azure-automation`, the same service principal that now has signer access.
- Confirmed GitHub repo vars:
  `AZURE_TRUSTED_SIGNING_ACCOUNT=wirawintrustsign` and
  `AZURE_TRUSTED_SIGNING_ENDPOINT=https://cus.codesigning.azure.net/`.
- GitHub repo var `AZURE_TRUSTED_SIGNING_CERT_PROFILE` is still unset, so the
  signing gate correctly remains off.

Current blocker: Ni Biashara LLC Organization identity validation is submitted
but not completed. The corrected Public Trust validation request is
`02ab1180-16dd-4c5d-b667-872c3db74b78`; the Microsoft vetting gateway now shows
status `InProgress` with OneVet request
`fb03644a-fb45-42bd-afe2-a5e3b5616a5f`. The earlier request
`0392d0e2-0046-4505-8a23-5f7aa4e09fc8` failed, in part because its website
field was malformed. The still older validation ID
`9df16837-7f54-4e41-b4da-05a7a9a06476` no longer works after account deletion;
Azure rejects it with `System could not find identity validation id`.

The Azure portal currently opens the correct account as `twe@nibiashara.biz`,
but the `Identity validations` blade renders an empty content area because the
portal's own vetting API calls are blocked by browser/CORS behavior. A direct
authenticated portal-gateway submission was used to create the corrected request.

The certificate profile is not created yet. Azure still rejects
`az artifact-signing certificate-profile create ... --identity-validation-id
02ab1180-16dd-4c5d-b667-872c3db74b78` with `System could not find identity
validation id`, which is consistent with Microsoft docs requiring the identity
validation process to finish before the ID can be selected for certificate
profile creation. Current Microsoft docs quote a public identity validation
processing time of 1 to 20 business days, with email or portal action required
if additional verification or documents are requested.

After validation reaches `Completed`: create Public Trust certificate profile
`wira-public-trust`, set repo var `AZURE_TRUSTED_SIGNING_CERT_PROFILE`, dispatch
a Windows build, then smoke-check the signed installer before removing the public
unsigned-beta warning.

### 2026-06-10 — security siege fixes + signing-ready build

A static red/blue/black-team audit (`/siege`) drove a hardening pass. All findings
fixed in code (67→71 agent tests pass; site typecheck/build + Worker dry-run clean):

- **Confirmation is now enforced, not cosmetic (C1).** `agent/runtime_bridge.py`
  only passes Hermes `--yolo` (auto-approve every tool call) when the owner picked
  the "move fast" mode. With confirmation required (the default/recommended choice)
  it runs without `--yolo`, so destructive/prompt-injected actions stop to ask. Added
  a subprocess timeout so a stuck call can't hang the WhatsApp handler.
- **Non-owner text can never reach the operator runtime (H1).** `agent/whatsapp.py`
  routes external/customer messages through a plain LLM responder (`Brain`), never the
  Hermes operator runtime — even if the legacy external responder mode is re-enabled.
- **Owner-lock is a hard invariant for the operator runtime (H2).** New
  `runtime_bridge.build_local_runtime()` (used by `main.py` + `gui.py`) refuses the
  Hermes operator runtime when owner-lock is off and falls back to the plain responder,
  so a flipped flag can't hand every sender shell access.
- **Supply chain (H3 + M3).** `build-windows.yml` now pins all actions to commit SHAs,
  pins Inno Setup, pins `neonize==0.3.18.post0`, and verifies the native Windows DLL by
  SHA-256 before bundling (a tampered/swapped upstream asset fails the build).
- **Webhook + site (M1/M2/L1–L3).** Cloud webhook binds loopback by default; site adds
  a Content-Security-Policy; Worker CORS is allowlisted (no arbitrary origin reflection),
  buyer PII is dropped from logs, and the download-source leak header is removed.
- **Historical signing note, now stale.** `build-windows.yml` has a guarded Azure
  Trusted Signing step. The account was provisioned on 2026-06-06/10, but it was
  deleted on 2026-06-28. Treat the 2026-07-09 section above as the current source
  of truth before attempting a signed Windows build.

### 2026-06-07 — cross-platform enablement progress

Wira is now genuinely Mac + Windows, not Mac-only sales copy over a Mac-only product:

- Fixed a real capability-detection bug: RAM was read via `os.sysconf`, which does
  not exist on Windows, so every Windows machine reported 0 GB and was forced into
  the limited local-AI tier. `agent/platform_support.py` now reads RAM correctly on
  macOS/Linux (`sysconf`) and Windows (`GlobalMemoryStatusEx` via `ctypes`);
  `agent/local_models.py` reuses that single helper.
- The Windows installer (`WiraSetup.exe`) is already produced by the release pipeline
  and verified present in releases v1.0.6 and v1.0.7, but public Windows downloads
  are paused until code signing completes and a clean Windows install smoke test
  passes. The Worker now returns a Windows coming-soon message instead of handing
  buyers an unsigned installer.
- `agent/gui.py` auto-start no longer assumes macOS (launchd plist is macOS-only;
  Windows uses the installer's Startup-folder shortcut).
- `agent/runtime_bridge.py` no longer hardcodes a founder-specific Hermes path; it
  discovers Hermes via PATH (cross-platform) or the standard `~/.hermes` install dir.
- Intel Mac decision (2026-06-10): explicitly OUT OF SCOPE — not the Wira user base.
  The Mac app stays Apple-Silicon-only (M1 or newer); no universal2 or x86_64 artifact
  will be built. `agent/wira.spec` builds host-arch (arm64) + bundles
  `neonize-darwin-arm64.dylib`, and the site copy states the Mac app requires Apple Silicon.
- Signing (2026-06-10): code signing is being provisioned out-of-band — the Azure Trusted
  Signing org identity validation for Ni Biashara is in progress. The build workflow is now
  signing-ready: a guarded Azure Trusted Signing step (see the 2026-06-10 siege section) signs
  `WiraSetup.exe` once the org's signing secrets/vars are registered. Until then the build still
  ships unsigned (early beta). Mac DMG notarization still pending. Creds are not yet in
  `credential_registry.json`; the handoff packet still requests them.
- Applied (2026-06-10): `.github/workflows/build-windows.yml` pins `neonize==0.3.18.post0`
  and downloads + SHA-256-verifies the matching native DLL, so the wrapper and DLL can't
  drift and a tampered upstream asset fails the build.

Verification on 2026-06-07: 67 agent unit tests pass; `site/` typecheck + build clean;
Worker `wrangler deploy --dry-run` bundles clean. NOT yet verified: a live Windows
install smoke test (launch → provider setup → QR pairing → restart persistence) and
code signing / notarization. Those need a real Windows box and signing certs.

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
- `docs/plans/2026-06-05-wira-cross-platform-enablement.md`

## Next production closeout

1. Finish the actual runtime bridge hardening so owner WhatsApp commands run through the real Wira/Hermes profile path with durable session/state receipts.
2. Replace any remaining advanced/admin docs that still describe legacy responder setup as the primary Local flow.
3. Rework the WhatsApp local transport so owner-issued messages become the primary command path.
4. Bridge Wira into a real Hermes runtime/profile instead of the current single-prompt reply generator.
5. Only then re-evaluate whether any responder/draft workflows remain worth keeping as an optional later mode.
