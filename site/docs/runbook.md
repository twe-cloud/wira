# Operator Runbook

The "how to actually run this" doc. Read once end-to-end before launch, then keep open for ops.

This is the **concierge-SaaS v1**: customers pay through the site, you (the operator) provision their assistant manually on a small VPS. ~15 minutes per customer. Sustainable for the first ~50 customers — beyond that, build automation (Stripe webhook → spin up instance).

---

## One-time launch checklist

### 1. Stripe
1. Create a Stripe account (test mode is fine for the first week).
2. **Products → Create product** → "WhatsApp Assistant" → add two recurring **Prices**: one monthly, one yearly.
3. Copy the two **Price IDs** (`price_*`) into `site/src/lib/brand.ts` → `PRICING.stripePriceMonthly` and `stripePriceAnnual`.
4. **Developers → API keys** → copy `sk_test_*` (or `sk_live_*` later) — set as `STRIPE_SECRET_KEY` in Netlify.
5. **Developers → Webhooks → Add endpoint** → URL: `https://<site>/.netlify/functions/webhook`. Pick events: `checkout.session.completed`, `customer.subscription.updated`, `customer.subscription.deleted`, `invoice.payment_failed`. Copy the **Signing secret** → set as `STRIPE_WHSEC` in Netlify.

### 2. Netlify
```bash
cd site
npm install -g netlify-cli
netlify login
netlify init                        # link this folder
# Set env vars (or do it in the Netlify dashboard)
netlify env:set STRIPE_SECRET_KEY sk_test_...
netlify env:set STRIPE_WHSEC whsec_...
netlify env:set SITE_URL https://<your-netlify-site>.netlify.app
npm run netlify:deploy:prod
```

### 3. DNS (when ready for a real domain)
Point your domain at Netlify, add the custom domain in the dashboard. Update `PRODUCT.domain` in `brand.ts`, regenerate `sitemap.xml` and `robots.txt`.

### 4. Email
1. Set up `hello@yourdomain.com` (or whatever `PRODUCT.supportEmail` is).
2. Sign up for a transactional email sender (Resend, Postmark, or Loops). Get the API key.
3. For v1 you'll send the activation email **manually** when a Stripe payment notification hits your inbox.

### 5. VPS for the first customer
Pick one: Hetzner CX11 (€4/mo), DigitalOcean $6 droplet, Fly.io. One VPS per customer in v1.
```bash
# On a fresh Ubuntu/Debian VPS:
ssh root@<ip>
adduser wira && usermod -aG sudo wira
su - wira
git clone https://github.com/<you>/<repo>.git
cd <repo>/wira-whatsapp
./scripts/install.sh
nano .env       # fill in OWNER_NAME, ANTHROPIC_API_KEY
# Start it temporarily to scan the QR
.venv/bin/python main.py
# (Customer scans QR from their phone)
# Ctrl-C, install as a service
sudo cp scripts/wira.service /etc/systemd/system/
sudo systemctl enable --now wira
journalctl -u wira -f
```

---

## New-customer provisioning (per signup)

You get a Stripe email "New subscription". Total time target: **15 minutes from payment to first reply.**

1. **(2 min)** Open the Stripe customer record. Grab their email and any name/notes.
2. **(2 min)** Spin a fresh VPS (or pre-keep a pool of warm ones). Note the IP.
3. **(3 min)** SSH in, clone the repo, run `./scripts/install.sh`. Edit `.env`:
   - `OWNER_NAME=<their first name>`
   - `ANTHROPIC_API_KEY=<from your shared pool>` (cost flows back through their subscription)
   - `APPROVAL_MODE=draft` (start safe; promote once they trust it)
   - `VOICE_SAMPLES_FILE=` (leave blank; they'll fill it in)
4. **(3 min)** Email them the activation link. Template:
   ```
   Hey [name] — welcome to [Product].
   Your assistant is ready. To activate:
   1. Click here: https://<your-site>/activate?token=<one-time-token>
   2. On your phone, open WhatsApp → Settings → Linked Devices → Link a Device.
   3. Scan the QR shown on the activation page.
   
   I'll be watching the first hour to make sure replies go out clean.
   Reply to this email if anything looks off.
   — [you]
   ```
   
   For v1 the activation page is a **terminal session you're watching** via tmux on the VPS — the QR prints there. (Roadmap: render the QR in a web page.)
5. **(2 min)** SSH in, `tmux attach`, run `.venv/bin/python main.py`. The QR appears.
6. **(2 min)** Customer scans. You see "Connected to WhatsApp as <name>" in the logs. Install as service:
   ```bash
   sudo cp scripts/wira.service /etc/systemd/system/
   sudo systemctl enable --now wira
   ```
7. **(1 min)** Tail logs for 5 minutes. First incoming message hits — verify the draft looks reasonable. Send a "looking good?" email.

### Promote a contact to auto-send
SSH in, `nano /home/wira/.../.env`, add to `AUTO_SEND_TO=...` (comma-separated phone numbers, digits only), `sudo systemctl restart wira`.

### Switch to auto-all (full trust)
`APPROVAL_MODE=auto-all` in `.env`, restart. Customer should explicitly request this.

### Switch to local LLM (Ollama)
On the VPS: `curl -fsSL https://ollama.com/install.sh | sh && ollama pull llama3.2:3b`. In `.env`: `LLM_PROVIDER=ollama`. Restart.

---

## Ongoing ops

### Monitor everything
```bash
# Per-customer health
ssh wira@<vps-ip> 'systemctl status wira && journalctl -u wira --since "1 hour ago" | tail -50'
```

A small ops script (`scripts/check-all.sh`) that ssh-loops over your VPSes is a good early invest. Run it twice a day until you trust the fleet.

### Common issues
- **"Session expired"** in logs → customer's phone was offline >14 days. Email them: "your assistant got disconnected, scan this fresh QR to reconnect."
- **Replies sound off** → check `VOICE_SAMPLES` is set. Ask customer to paste 5 more of their recent messages, drop them into `voice.txt`, restart.
- **Anthropic 429 / quota** → check usage at console.anthropic.com. Move heavy users to a per-customer key.
- **WhatsApp ban** (rare) → only happens on bulk outreach. Customer chose `auto-all` and was used as a spam tool? Suspend, refund, document.

### Backups
Each VPS holds `session.sqlite3` (WhatsApp pairing) and `~/.wira/memory.db` (conversation memory). Nightly:
```
0 3 * * * rsync -a --delete /home/wira/wira-whatsapp/session.sqlite3 /home/wira/.wira/ backup@<your-backup-host>:backups/<customer>/
```

### Refund / cancel
Customer hits cancel in their Stripe customer portal. Stripe webhook fires `customer.subscription.deleted` (logged in `webhook.ts`). At end of paid period:
1. SSH in, `sudo systemctl stop wira && sudo systemctl disable wira`.
2. Wipe data: `rm -rf /home/wira/wira-whatsapp /home/wira/.wira`.
3. Decommission VPS.

For partial-month refunds: judgement call. Stripe makes refunds easy. Default: no, except for unused yearly time or genuine product failure.

---

## What's NOT built yet (roadmap, in rough order)

1. **Hosted web dashboard** — customer logs in, sees drafts, approves with one click. (Currently drafts live in `drafts.db`; you read them from logs or directly.)
2. **Magic-link email automation** — Stripe webhook → spin up VPS → email customer with QR URL. (Currently manual.)
3. **Web-rendered QR** — show the WhatsApp QR in a browser instead of terminal. (Currently terminal only.)
4. **Voice transcription** — answer voice notes. (Currently text only.)
5. **Multi-tenant** — N customers per VPS instead of 1:1. (Big infra change; defer until ~50 customers.)
6. **BYO API key** — customer pastes their own Claude/OpenAI key. (Lower price point, no Anthropic cost on us.)

When you have 10+ paying customers, start with (3) — that's the biggest UX cliff in the current flow.
