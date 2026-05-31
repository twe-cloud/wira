# Wira

Your AI assistant, living on your WhatsApp.

People message your number. **Wira** answers — in your voice, instantly, around the
clock. It remembers every conversation, handles the small stuff, and knows when to hand a
chat back to you. *Wira* is Swahili for hero — the kind that quietly does the work.

No new app for anyone to install. No new number to share. It runs on the WhatsApp people
already use to reach you.

## What It Looks Like

```
Friend:  yo is craig around this weekend? thinking of pulling up
Wira:  He's mostly free Saturday — Sunday's looking packed though. Want me to
         flag it to him so he locks it in?
Friend:  yeah do that
Wira:  Done, he'll confirm a time with you directly. 🤝

Client:  Hi, are you available for a quick call tomorrow?
Wira:  Likely yes — mornings are better for him. I'll have Craig confirm the exact
         slot so nothing clashes. What's the call about, so I can brief him?
```

Short, warm, on-brand. It mirrors how each person talks to you, and it never makes a
promise it shouldn't — anything real gets escalated back to you.

## What Makes Wira Different

- **It's your actual number.** Links to your personal WhatsApp via QR, like WhatsApp Web.
  Nobody downloads anything. That's why the demo lands every time.
- **Remembers per person.** Every contact gets their own thread of memory, so conversations
  pick up where they left off — not goldfish-brained like most bots.
- **Knows its lane.** Built-in guardrails: never commits to meetings/money/promises on your
  behalf, never leaks your private details, escalates anything sensitive to you.
- **Your brain, your choice.** Runs on Claude (best quality) or a fully local model via
  Ollama (private, free, never leaves your machine).
- **Ignores manipulation.** Messages that try "ignore your instructions" tricks get shut down.

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

Point the Meta webhook subscription at:

```text
https://<your-host>/webhooks/whatsapp
```

The webhook verifies Meta's challenge token, verifies `X-Hub-Signature-256` by default,
ignores delivery-status callbacks, deduplicates inbound message IDs, and routes customer
text into the same Wira brain/memory/draft policy as the local QR version.

For the managed small-business product, keep two SKUs separate:

| SKU | Channel | Best for |
|---|---|---|
| Wira Local | QR-linked personal WhatsApp | Founder/personal assistant, demo, private local use |
| Wira Business | WhatsApp Business Cloud API | Managed AI assistants on dedicated business numbers |

Provider note: Twilio can still be useful for number procurement or as a WhatsApp BSP,
but Wira Business should stay provider-abstracted. Direct Meta Cloud API and Twilio
WhatsApp are different transports with different credentials, callbacks, and operational
controls.

## Offering Wira as a Setup

This repo is the product. Two ways to sell it:

1. **Done-for-you setup.** You run `install.sh` on their box (or a small VPS), link their
   number, tune `OWNER_NAME` and the persona in `prompts.py` to their voice, hand over the
   keys. Charge for setup + a monthly minding fee.
2. **Self-serve.** Hand them this repo and the Quick Start. You sell support and persona
   tuning.

The persona in `prompts.py` is the part worth customising per client — that's where Wira
stops sounding generic and starts sounding like *them*.

## License

MIT
