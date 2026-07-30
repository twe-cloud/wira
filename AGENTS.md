# Wira — Agent Context

Lane: BUSINESS. Canonical path: `/Users/motwe/Wira`. Remote:
`git@github.com:twe-cloud/wira.git`.

## What this project is
Wira is the productized WhatsApp assistant lane for small businesses, sold as
two SKUs: **Wira Local** (`agent/`, Python) — a QR-linked personal-WhatsApp
agent living on the buyer's machine — and **Wira Business**, the same brain
reached over Meta's official WhatsApp Business Cloud API for managed
deployments. Distribution is a notarized Mac app (Apple Silicon only) and
signed Windows installers; `site/` is the marketing/onboarding/checkout site.

## Canonical paths
- `agent/` — Python runtime: `main.py` (entry), `gui.py`, `runtime_bridge.py`
  (owner-lock + Hermes bridging), `whatsapp.py`/`whatsapp_cloud.py`/
  `cloud_webhook.py`, `tests.py`.
- `site/` — Vite+React SPA and Cloudflare Worker (`site/cloudflare/worker.ts`)
  serving `/api/checkout`, `/api/webhook` (Stripe), `/download/*`. Config:
  `site/wrangler.jsonc` (`name: wira-local-agent`, domain
  `wira.nibiashara.biz`).
- `scripts/` — `preflight.sh` (run before work), `qa.sh` (release-readiness
  suite), `verify-authenticode.py` (verify signed Windows asset).
- `docs/qa/windows-smoke-checklist.md` (required human pass before any public
  Windows release) and `.github/workflows/deploy-worker.yml` (auto-
  `wrangler deploy` after CI passes on `main`).

## Hosting truth
Cloudflare Workers, not Netlify. `site/wrangler.jsonc` name is
`wira-local-agent`; STATUS.md confirms the move off Netlify on 2026-06-03.
Live: `https://wira-local-agent.nibiashara.workers.dev` and
`https://wira.nibiashara.biz`.

## Build / run / test (evidenced)
- `site/`: `npm run dev` · `npm run build` · `npm test` (vitest) ·
  `npm run cf:dev` (`wrangler dev`) · `npm run deploy`.
- `agent/`: `pip install -r requirements.txt`; `python3 -m unittest -q` from
  `agent/` (77 pass locally per STATUS.md).
- Run `scripts/preflight.sh` then `scripts/qa.sh` before calling anything
  release-ready.

## Gotchas, hard rules, and no-touch list
- Trusted Signing certs are short-lived (~3 days); the RFC3161 timestamp
  keeps signed binaries valid past expiry — not a bug.
- Intel Macs are out of scope; Apple Silicon only, no universal2/x86_64.
- `cloud_webhook.py` forces the `business_cloud` prompt profile — Hermes must
  never appear in customer-facing chat.
- Sales-safe wording (STATUS.md): never claim "fully unattended" or a live
  standalone Wira Business host until that deployment is smoke-tested.
- Windows release order: smoke checklist on real hardware, tagged release
  with signed asset, `verify-authenticode.py` check, then flip
  `/download/windows`.
- Do not touch `agent/scripts/rebuild-and-resubmit.sh` /
  `ship-direct-download.sh` (gitignored; embed keychain password + signing
  key paths) or `site/.dev.vars` (local secrets; never log or commit).
- Do not run `wrangler deploy` or push without same-session approval;
  `deploy-worker.yml` already auto-ships from CI.

See `/Users/motwe/AGENTS.md` for estate-wide rules, `STATUS.md` here for current release state.
