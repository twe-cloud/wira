# Wira live proof — 2026-06-04

## Deployed surface
- Worker URL: https://wira-local-agent.nibiashara.workers.dev
- Worker version: `ffb3b33a-9219-4e87-ad31-b9866e7a69d8`
- Deploy command: `npm run deploy`
- Result: success

## Local validation before deploy
- `python3 -m unittest -q` in `agent/`: 55/55 passing
- `npm run build` in `site/`: passing

## Business surface gate
- Command: `python3 /Users/motwe/Control Room/scripts/business_surface_gate.py https://wira-local-agent.nibiashara.workers.dev/`
- Result: `BUSINESS_SURFACE_GATE_PASS`
- Widths checked: 320, 375, 414, 768, 1280

## Live proof checks completed

### 1) Landing page copy
Verified live on the deployed Worker:
- headline: `Your first personal agent, reached from WhatsApp.`
- free-first positioning is present
- ChatGPT remains visible as an option
- Apple Silicon Mac-only warning is visible
- journey order is visible as:
  1. Download Wira
  2. Pick your brain
  3. Connect WhatsApp

### 2) Checkout session creation
Verified against live Worker:
- `POST /api/checkout` with `priceId=price_1TcrAXRVrXHv0YFpfmw35hIw` returned a live Stripe Checkout URL
- same-origin browser fetch from the deployed site also returned a live Stripe Checkout URL

### 3) Stripe checkout page content
Verified on the returned live Stripe Checkout page:
- title: `Stripe Checkout`
- product title: `Wira`
- product body: `Your own AI agent on WhatsApp. Start free, connect ChatGPT, or keep it private on your Mac.`
- promotion code field is present: `Add promotion code`
- amount due: `$49.00`

### 4) Success page
Verified live at `/success?session_id=cs_live_PROOF123456789`:
- 3-step success checklist is present
- step 1: download and open Wira
- step 2: pick a brain
- step 3: scan the WhatsApp QR
- stable download link is shown on-page
- receipt reference renders from `session_id`
- generic `Get started` CTA is hidden on this page

### 5) Download route
Verified live download path:
- URL: `https://wira-local-agent.nibiashara.workers.dev/download/wira-mac`
- HTTP: 200
- content-type: `application/octet-stream`
- content-disposition: `attachment; filename="Wira.dmg"`
- source header: `x-wira-download-source: https://github.com/twe-cloud/wira/releases/latest/download/Wira.dmg`
- downloaded artifact: `/tmp/wira_live_proof.dmg`
- byte size: `36342420`
- sha256: `2a7d87f0ed212568eccb92614d0310eb4d8b7cb07013337f1564068fb4b6af4e`

### 6) Onboarding flow
Verified live at `/onboarding`:
- step 1 welcome is download-first
- step 2 brain selection is free-first, ChatGPT visible, private local optional
- Groq free-key link is present
- WhatsApp step tells the user to open Wira first and pair through Linked Devices
- final ready step gives first-message examples and download/reopen path
- localStorage persistence is working: revisiting `/onboarding` returned to `Step 5 of 5 · Ready`

## Important remaining truth
These are still the live-proof limits:
- I did not complete a real payment.
- I did not complete a real WhatsApp QR scan with the desktop app in this browser proof.
- I did not send a first real WhatsApp message through a freshly paired live install in this run.

## Public-link warning
`https://nibiashara.biz/products/wira/` is still a different, older Netlify-hosted page and does **not** match the newly deployed Worker experience.

For a friend test of the flow validated here, use the Worker URL above — not the current `nibiashara.biz/products/wira/` page.
