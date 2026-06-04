**Verdict: FAIL**

The current fix is not enough. The copy direction mostly matches the intent, but the buyer path still fails on the download/release gate.

**Findings**

| Area | Result | Evidence |
|---|---:|---|
| Download bottleneck | FAIL | [site/wrangler.jsonc](/Users/motwe/Wira/site/wrangler.jsonc:15) only runs the Worker first for `/api/*`, but the new download endpoint is `/download/wira-mac` in [worker.ts](/Users/motwe/Wira/site/cloudflare/worker.ts:15). With SPA asset fallback, `/download/wira-mac` can serve the app shell instead of `handleDownload`. Cloudflare’s docs say selective `run_worker_first` paths are what force Worker-script routing. |
| Release artifact | FAIL | Local `agent/dist/Wira.dmg` exists and `hdiutil verify` passed, but `codesign --verify --deep --strict agent/dist/Wira.app` failed: `invalid signature (code or signature have been modified)`. `spctl` on the DMG also failed with an internal Code Signing subsystem error. Do not call this buyer-ready. |
| Fake/live claims | FAIL | [Success.tsx](/Users/motwe/Wira/site/src/pages/Success.tsx:20) says “your agent is live on WhatsApp” before download, brain choice, QR pairing, or first message has happened. [worker.ts](/Users/motwe/Wira/site/cloudflare/worker.ts:271) repeats “your agent is live” in the email copy. |
| Free option first | PASS, with caveat | Website onboarding puts free first at [Onboarding.tsx](/Users/motwe/Wira/site/src/pages/Onboarding.tsx:176), and GUI puts free API first at [gui.py](/Users/motwe/Wira/agent/gui.py:306). Caveat: [Learn.tsx](/Users/motwe/Wira/site/src/pages/Learn.tsx:98) still lists local model before API key. |
| ChatGPT clarity | PASS | ChatGPT is still explicit in onboarding [Onboarding.tsx](/Users/motwe/Wira/site/src/pages/Onboarding.tsx:185), success [Success.tsx](/Users/motwe/Wira/site/src/pages/Success.tsx:46), and GUI [gui.py](/Users/motwe/Wira/agent/gui.py:335). |
| Local/private preserved, not default | PASS for main GUI/site, PARTIAL repo drift | Main GUI/site make local/private available but third. However [agent/setup.py](/Users/motwe/Wira/agent/setup.py:35) still says ChatGPT is easiest and default/recommended, and README config still references Anthropic/Claude defaults at [agent/README.md](/Users/motwe/Wira/agent/README.md:81). |
| Checkout → success → download → onboarding → WhatsApp | FAIL | Checkout/success/onboarding copy is more intuitive, but the download link can miss the Worker, live link could not be verified from this sandbox, and the local app signature is invalid. |

**Remaining Risks**

The biggest risk is a paid buyer landing on `/success`, clicking “Download for Mac,” and getting either the SPA shell, a missing GitHub asset, or a DMG containing an app Gatekeeper rejects.

Exact next files/flows to fix:

1. [site/wrangler.jsonc](/Users/motwe/Wira/site/wrangler.jsonc:15): add `/download/*` to `run_worker_first`.
2. [site/src/lib/brand.ts](/Users/motwe/Wira/site/src/lib/brand.ts:20): prefer same-origin `/download/wira-mac` unless there is a strong reason to hardcode workers.dev.
3. [agent/dist/Wira.app](/Users/motwe/Wira/agent/dist/Wira.app): rebuild, sign, notarize, staple, then re-run `codesign`, `spctl`, `stapler`, and upload the exact DMG.
4. [site/src/pages/Success.tsx](/Users/motwe/Wira/site/src/pages/Success.tsx:20) and [worker.ts](/Users/motwe/Wira/site/cloudflare/worker.ts:271): replace “agent is live” with “you are ready to set it up” until QR + first WhatsApp message are proven.
5. [agent/setup.py](/Users/motwe/Wira/agent/setup.py:30) and [agent/README.md](/Users/motwe/Wira/agent/README.md:75): align CLI/support docs with free-first, ChatGPT-clear, private-available positioning.

**Verification Run**

`npm run build` in `site/` passed.  
`python3 -m unittest agent.tests` aborted in Tk GUI construction under this shell, so GUI test verification is not clean.  
`npm run cf:dev`, `curl`, and `gh release view` could not verify live routes because sandbox DNS/loopback/network access is blocked.  
Cloudflare routing reference used: https://developers.cloudflare.com/workers/static-assets/routing/worker-script/

