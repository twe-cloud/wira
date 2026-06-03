# Wira

Your first personal agent, reached from WhatsApp.

Wira is not meant to be a glorified reply bot. The real thesis is simpler and
stronger: **Wira** is a branded path into a real local Hermes agent that lives
on your computer and is easiest to engage from your phone.

That means:

- **Phone-first, computer-real.** You pair over WhatsApp so the first interaction feels familiar, but the real runtime lives on your machine.
- **A bridge out of plain chat.** The buyer starts from a simple branded surface, then organically discovers Hermes Desktop, CLI, tools, skills, and local access over time.
- **Owner/operator first.** The primary user is the owner talking to their own agent, not a public customer-reply lane by default.
- **Vera by default.** The local starter identity can be friendly and branded, with rename available after setup.

## What It Looks Like

```
You:   what's left on my calendar after 2pm?
Vera:  You have a client check-in at 3:30 PM and a design review at 5 PM.
       Want a short prep brief for both?

You:   search Downloads for the latest invoice PDF
Vera:  Found the newest invoice PDF in Downloads. I can open it, summarize it,
       or prep an email around it next.
```

Short, useful, grounded in real work. The goal is that Wira starts simple and
then grows with the user into a deeper Hermes workflow.

## What Makes Wira Different

- **It's the easiest first step into a real agent.** No need to begin with terminal tabs, profiles, or agent jargon.
- **It still grows into Hermes.** Wira should not trap the buyer in a toy layer; it should gradually reveal the deeper runtime and tools.
- **Lives on the buyer's machine.** The local path is about ownership, not another hosted chat widget.
- **WhatsApp is the command surface, not the whole product.** The value is the local agent underneath.
- **Your brain, your choice.** Runs on ChatGPT, Claude, GPT, or a fully local model via Ollama.

## Quick Start

```bash
git clone https://github.com/nkongecraig-max/claude-creations.git
cd claude-creations/wira-whatsapp
./scripts/install.sh
```

Set your key:

```bash
nano .env
# LLM_PROVIDER=anthropic
# ANTHROPIC_API_KEY=sk-ant-...
# OWNER_NAME=Craig
```

Start Wira and link your phone:

```bash
.venv/bin/python main.py
# A QR code prints in the terminal.
# On your phone: WhatsApp > Settings > Linked Devices > Link a Device > scan it.
```

That's it. Message the number from another phone and Wira replies.

Run it as a service so it survives reboots:

```bash
sudo cp scripts/wira.service /etc/systemd/system/
sudo systemctl enable --now wira
journalctl -u wira -f   # watch it work
```

## Configuration

Everything lives in `.env`:

| Setting | What it does | Default |
|---|---|---|
| `LLM_PROVIDER` | `anthropic` (Claude) or `ollama` (local) | `anthropic` |
| `ANTHROPIC_API_KEY` | Your Claude API key | — |
| `LLM_MODEL` | Override the model | `claude-sonnet-4-6` |
| `OWNER_NAME` | Who Wira represents | `Craig` |
| `REPLY_TO_GROUPS` | Answer in group chats too | `false` (DMs only) |
| `ALLOWLIST` | Only reply to these numbers (digits, comma-separated) | everyone |
| `DISCLOSE_AI` | Admit it's an AI when asked | `true` |

### Want it fully private?

```bash
# Install Ollama, then in .env:
LLM_PROVIDER=ollama
LLM_MODEL=llama3.2:3b
```

Nothing leaves the machine. Slower and a little less sharp than Claude, but yours alone.

## Stack

| Component | Tool |
|---|---|
| WhatsApp link | neonize (whatsmeow) — QR multi-device |
| Brain | Claude (Anthropic) or Ollama (local) |
| Memory | SQLite, per-contact |
| Runtime | Python 3.10+ |

## Going Bigger: Official WhatsApp Business API

The QR-link setup above uses your **personal** number — perfect for yourself, a demo, or a
solo operator. It's the unofficial multi-device protocol, so treat it like a personal tool,
not a 10,000-contact broadcast machine (heavy automated use on a personal number can get it
flagged).

For a business doing real volume, the clean path is Meta's **WhatsApp Business Cloud API**:
official, unbannable, scalable, on a dedicated business number. Same Wira brain
(`brain.py` / `memory.py` / `prompts.py`) — only the transport layer (`whatsapp.py`) swaps
out for a webhook. That's the natural "Wira Pro" tier.

This repo now has that transport:

```bash
# Server-side only. Do not ship these in the desktop app.
WHATSAPP_CLOUD_ACCESS_TOKEN=...
WHATSAPP_CLOUD_PHONE_NUMBER_ID=...
WHATSAPP_CLOUD_VERIFY_TOKEN=...
WHATSAPP_CLOUD_APP_SECRET=...
WHATSAPP_CLOUD_REQUIRE_SIGNATURE=true

python cloud_webhook.py
```

In the Motwe / Ni Biashara workspace, the same server also accepts the shared
Meta credential-profile names used by `credential_guard.py`:

```bash
WHATSAPP_ACCESS_TOKEN=...
WHATSAPP_PHONE_NUMBER_ID=...
WHATSAPP_WEBHOOK_VERIFY_TOKEN=...
WHATSAPP_APP_SECRET=...
```

Sales truth: Wira Business is sold as a managed per-business deployment using
the live-proven Ni Biashara Cloud API pattern. Do not claim a customer-specific
standalone Wira Business host is live until that deployment has passed webhook
challenge verification, signed inbound-message verification, draft creation,
and an owner-approved outbound send.

Point the Meta webhook subscription at:

```text
https://<your-host>/webhooks/whatsapp
```

The webhook verifies Meta's challenge token, verifies `X-Hub-Signature-256` by default,
ignores delivery-status callbacks, deduplicates inbound message IDs, and routes customer
text into the same Wira brain/memory/draft policy as the local QR version.

Customer-facing identity is different on the Cloud path. `cloud_webhook.py` forces the
`business_cloud` prompt profile:

- WhatsApp customers see and hear from the client's business identity, controlled by the
  WhatsApp Business display name and `BUSINESS_NAME`.
- Wira is the owner/admin product name and operator feed, not the default customer-facing
  speaker.
- Hermes is internal plumbing only and must not appear in customer or client-facing chat.
- Set `CUSTOMER_VISIBLE_ASSISTANT_NAME` only when the business explicitly wants a named
  assistant such as Nia.

For the managed small-business product, keep two SKUs separate:

| SKU | Channel | Best for |
|---|---|---|
| Wira Local | QR-linked personal WhatsApp | Founder/personal assistant, demo, private local use |
| Wira Business | WhatsApp Business Cloud API | Managed AI assistants on dedicated business numbers |

Provider note: Twilio can still be useful for number procurement or as a WhatsApp BSP,
but Wira Business should stay provider-abstracted. Direct Meta Cloud API and Twilio
WhatsApp are different transports with different credentials, callbacks, and operational
controls.

## Updates

Wira Local stores user-owned config, auth, WhatsApp pairing, memory, drafts, and onboarding
state in `~/.wira`. The app can be replaced without bundling customer data into the app
folder.

To update a Local install, download the latest Mac or Windows build from:

```text
https://github.com/twe-cloud/wira/releases/latest
```

If a WhatsApp linked-device session expires, reconnect from the Wira window and scan a new
QR code. The buyer controls their machine, accounts, tools, model/provider cost, and
message behavior.

## Offering Wira as an Enablement Setup

This repo is the product. Two ways to sell it:

1. **Done-for-you setup.** You run `install.sh` on their box (or a small VPS), link their
   number, tune `OWNER_NAME` and the persona in `prompts.py` to their voice, then hand over
   control.
2. **Self-serve.** Hand them the installer and setup guide. After setup, their agent is
   their responsibility.

The persona in `prompts.py` is the part worth customising per client — that's where Wira
stops sounding generic and starts sounding like *them*.

## Buyer-Facing Position

Wira Local is sold as enablement: install, connect, scan, configure, and hand control to
the buyer. Do not describe the buyer relationship as an ongoing software license, managed
support plan, hosted service, or uptime promise unless a separate written service is sold.
