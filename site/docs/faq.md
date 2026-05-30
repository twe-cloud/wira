# FAQ

## Setup

### How long does setup take?
Five minutes. Pay → choose voice + contact rules → scan the QR. The first reply usually goes out within 10 minutes of signup.

### Can I use it with a business WhatsApp number?
Yes — anything that works in WhatsApp Web works here. For high volume (>500 outbound msgs/day), we recommend the WhatsApp Business Cloud API instead. Email us about that path.

### Do I need to install anything?
No. The assistant runs on our servers. Your only step is scanning the QR from your phone.

## Voice and replies

### Will it sound like me?
After you paste 3-5 samples, yes. It mirrors phrasing, emoji use, formality, and length. You can refine the tone at any time from the dashboard.

### What if it says something wrong?
By default it drafts every reply and pings you to approve. You only auto-send to contacts you explicitly trust. There's also a global pause button.

### Does it tell people it's an AI?
If asked, yes — politely and briefly. You can change this in Settings if you prefer it not to volunteer.

### Can it remember what I told someone last week?
Yes — that's the whole point. Each contact has their own memory thread. You can view, export, or delete it any time.

## Privacy and safety

### Are my chats sent to OpenAI/Anthropic?
We use Claude by default. Per Anthropic's policy, your data is not used to train their models. Prefer fully local? Switch to Ollama mode — chats never leave your machine.

### Can your team read my messages?
No, not in normal operation. For support requests, you can grant temporary, time-boxed access from your dashboard. We log every such access.

### Where is the data hosted?
EU (Frankfurt) by default. We can move you to another region on Enterprise plans.

### What if I want to delete everything?
One button in Settings → Delete account. Erases conversation memory, profile, and stored messages within 24 hours. Billing records are kept for tax purposes only.

## WhatsApp

### Will WhatsApp ban my number?
We pair using the same multi-device protocol WhatsApp Web uses. We don't send unsolicited messages, we rate-limit naturally, and we recommend against bulk outreach. Same risk profile as keeping WhatsApp Web open. We can't make absolute guarantees — WhatsApp's policy is theirs to enforce.

### Does it reply in group chats?
Off by default. Turn on per-group from Settings. We recommend keeping groups off and only enabling specific ones.

### What about voice notes and images?
v1 handles text only. Voice-note transcription is on the roadmap.

## Billing

### When am I charged?
On signup, then monthly (or yearly if you chose annual). You can cancel any time from the dashboard.

### Do you offer refunds?
Not for partial months, but we'll review unusual cases. Email support and we'll work it out.

### Can I pause my subscription?
Yes — pause for up to 90 days from Settings. We stop billing during the pause; your assistant goes dormant.

### Is there a free trial?
Not currently. The single low-friction tier and cancel-anytime policy are our equivalent.

## Limits and roadmap

### How many messages can it handle?
A reasonable personal volume (low thousands per month). If you're sending tens of thousands, you want the WhatsApp Business Cloud API tier (talk to us).

### What's on the roadmap?
- Voice-note transcription + reply
- Native iOS / Android dashboards
- Calendar integration (one tap to confirm meetings)
- Multi-number support (handle several WhatsApps from one dashboard)
- Bring-your-own-API-key tier
