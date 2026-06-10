# Wira — Pre-launch checklist

What must be true before turning on paid traffic, and the tests that prove it.
Code-level tests now run in CI (`.github/workflows/ci.yml`). The items below are
the ones that need real hardware, live accounts, or an ops action — they can't be
fully automated from the repo.

## Now covered by automated CI (every PR)
- ✅ Agent unit suite (`agent/`, `python -m unittest`) — provider selection, send/draft
  policy, Meta webhook signature, owner-lock, non-owner→responder isolation, `--yolo`
  gating, memory pruning, runtime timeout, provider base-URL guard, onboarding.
- ✅ Worker unit suite (`site/cloudflare/worker.test.ts`, vitest) — CORS allowlist,
  open-redirect guard (`sanitizeSiteBase`), price validation, webhook signature guard,
  download-source fallback, method guards.
- ✅ Site typecheck + production build; Worker `wrangler deploy --dry-run`.
- ✅ Secret scan over source **and built artifacts** (`scripts/check-no-secrets.sh`).
- ✅ Supply chain: CI actions SHA-pinned; neonize native DLL verified by SHA-256.

## Launch-blocking — needs a human / hardware

### 1. First-run smoke on real machines
The product has never been run end-to-end on a clean machine. Do both:
- **Windows** (`docs/qa/windows-smoke-checklist.md`): install → launch → pick brain →
  scan QR → send a WhatsApp message → get a reply → quit → relaunch → still paired →
  message still works.
- **Mac** (Apple Silicon, after notarization): same flow + Gatekeeper accepts the app
  with no "unidentified developer" block.

### 2. Money path, verified once live
- Stripe **test mode** E2E: Buy → `4242 4242 4242 4242` → `/success` → webhook received
  → download email delivered. (Automate later with Playwright + `stripe listen`.)
- Rotate the full-access live `STRIPE_SECRET_KEY` to a **restricted key** scoped to
  Checkout Sessions: Write (+ the reads the Worker does). Re-set via `wrangler secret put`.
- Confirm the webhook is **idempotent** on Stripe redelivery (it retries on non-2xx).

### 3. Safe defaults in the shipped build
Verify a fresh install defaults to: owner-lock **on**, confirmation **on**
(so Hermes runs without `--yolo`), and the **balanced** (not operator) permission preset.

### 4. Code signing
- Windows: finish Azure Trusted Signing org validation → Public Trust cert profile →
  set `AZURE_TRUSTED_SIGNING_CERT_PROFILE` (SP + secrets already provisioned). Drop the
  SmartScreen "unsigned beta" note from the site once signed.
- Mac: Developer ID sign + notarize the DMG (cert + notarytool key are on the build Mac;
  see `agent/scripts/rebuild-and-resubmit.sh`).

## Strongly recommended before scaling

- **Alerting**: Worker observability is on, but nothing pages on 5xx / webhook signature
  failures. Add Logpush or Sentry + an alert. A silent webhook failure loses customers.
- **Rate-limit `/api/checkout`**: it mints Stripe sessions unauthenticated. Add a
  Cloudflare rate-limiting rule (dashboard) or a Workers rate-limit binding.
- **Pin the download**: the Worker proxies the *latest* GitHub release, so a bad release
  auto-propagates to buyers. Serve a known-good pinned tag and bump deliberately.
- **Synthetic uptime**: `GET /` (200), `OPTIONS /api/checkout` (204), `HEAD /download/*`
  (200) every few minutes → alert. Plus a weekly test-mode checkout canary.
- **Privacy/Terms**: have counsel review (templates note this). Copy now matches the
  local-first architecture (no server-stored conversations).

## Not worth it for v1
Load testing (low initial traffic), exhaustive LLM-provider matrix (smoke each once),
full browser/device matrix.
