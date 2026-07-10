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
- ✅ Windows installer signature, silent per-user install, install-tree layout,
  Windows RAM detection, and uninstall (`.github/workflows/windows-smoke.yml`,
  runs automatically after every `Build Windows Installer`).

Run all of the above locally in one shot with `./scripts/qa.sh`. It prints a
scoreboard, exits non-zero on any failure, and lists the human-only checks below
rather than skipping them silently. Add `--exe <path>` to also verify a signed
installer from a build box that has no `signtool` (`scripts/verify-authenticode.py`).

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
- ✅ **Windows: done (2026-07-10).** Org identity validation completed, Public Trust
  cert profile `wira-public-trust` created, `AZURE_TRUSTED_SIGNING_CERT_PROFILE` set.
  `build-windows.yml` now produces a signed, timestamped `WiraSetup.exe`, and
  `windows-smoke.yml` verifies the signature on every build.
- ✅ **Mac: done.** The shipped `Wira.dmg` is notarized — `spctl` reports
  `accepted / Notarized Developer ID / Developer ID Application: Ni Biashara llc
  (Y5XRB2L24U)`. Re-verify after any rebuild: `spctl -a -t open --context
  context:primary-signature -vv Wira.dmg`.
- ⛔ Still blocking the public Windows download: the signed installer lives only as a
  workflow artifact. Release `v1.0.7` still carries the **unsigned** `WiraSetup.exe`
  from 2026-05-31. Pass the Windows smoke checklist, cut a tagged release, then flip
  the Worker route.

## Strongly recommended before scaling

- **Alerting**: Worker observability is on, but nothing pages on 5xx / webhook signature
  failures. Add Logpush or Sentry + an alert. A silent webhook failure loses customers.
- **Rate-limit `/api/checkout`**: it mints Stripe sessions unauthenticated. Add a
  Cloudflare rate-limiting rule (dashboard) or a Workers rate-limit binding.
- **Pin the download**: the Worker proxies the *latest* GitHub release, so a bad release
  auto-propagates to buyers. Serve a known-good pinned tag and bump deliberately.
- **Synthetic uptime**: `GET /` (200), `OPTIONS /api/checkout` (204), `HEAD /download/mac`
  (302), and `HEAD /download/windows` (202 until launch) every few minutes → alert.
  Plus a weekly test-mode checkout canary.
- **Privacy/Terms**: have counsel review (templates note this). Copy now matches the
  local-first architecture (no server-stored conversations).

## Not worth it for v1
Load testing (low initial traffic), exhaustive LLM-provider matrix (smoke each once),
full browser/device matrix.
