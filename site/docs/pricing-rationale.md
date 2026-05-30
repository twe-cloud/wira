# Pricing rationale

Why **Wira costs $29/month** ($290/year, save 2 months).

## What competitors charge (2026)

| Product | Price | What you actually get |
|---|---|---|
| Martin AI (closest peer) | $21/mo standard, $30/mo Pro | Personal AI assistant for inbox + calendar + texts |
| Pi (Inflection) | Free | Generic personal AI, no WhatsApp integration |
| Wati | $39–99/mo + WhatsApp message fees | B2B WhatsApp chatbot platform (5+ users) |
| AiSensy | $18+/mo (India-focused) | B2B broadcast + chatbot |
| Respond.io | $45+/mo (chatbot extra $40) | B2B WhatsApp inbox |
| Personal.ai | $40+/mo | Generic "AI you" trained on your content |
| WhatsApp Writing Help | Free, in-app | Single-message draft suggestions (no memory, no autonomy) |

Sources at the bottom.

## What it actually costs us to run a customer (COGS)

For one user on the Claude Sonnet 4.6 brain at typical solo volume:

- Avg incoming message: ~50 tokens. Avg reply generated: ~60 tokens.
- System prompt + persona + voice samples + recent history per call: ~2,000 tokens.
- Claude Sonnet 4.6 pricing: **$3/M input, $15/M output**. Prompt caching cuts the static portion to 10%.
- Effective per-reply cost with caching: **~$0.002**.

| Daily replies | Monthly LLM cost | + VPS + Stripe | Total COGS |
|---|---|---|---|
| 50 (light) | ~$3 | $5 + $1 = $6 | **~$9** |
| 200 (typical solo) | ~$12 | $5 + $1 = $6 | **~$18** |
| 500 (heavy) | ~$30 | $5 + $1 = $6 | **~$36** |

At $29/mo, the typical solo user is ~38% gross margin. Heavy users (rare) cost us ~$7 — manageable. We tighten by:

1. Aggressive prompt caching (already designed into the prompt structure).
2. Capping at 1,000 replies/day in plan (above this, customer wants the "Pro" tier when it ships).
3. Moving heavy users to a per-customer Claude API key (planned BYO tier at $19/mo).

## Why one tier (no Basic / Pro / Enterprise)

The UX brief was emphatic: three-column pricing reads as "which one is the trap" for solo operators. **One price, one promise, annual saves 2 months.**

If we need a higher tier later, it's the "Pro" with voice-note transcription, multi-number support, and a dedicated brain. We'll know we need it when we have 50+ paying customers asking for one specific feature.

## Why not cheaper

- $19 puts us into "is this a real product?" territory for a SaaS that talks to your contacts. Premium pricing signals trust.
- $19 forces same-as-COGS margin for any user above 100 replies/day. Untenable.
- Annual is where the volume comes from anyway: $290/yr is 17% off, and yearly payers are 3× lower churn.

## Why not $39 or $49

- $39+ requires being noticeably better than Martin AI ($21–30). At launch we're not.
- The "under $30" psychological barrier matters for impulse signup; the conversion gap from $29 → $39 is consistently ~25% in the consumer-SaaS data.

## What the future tiers look like

| Tier | Price | Who it's for | When to ship |
|---|---|---|---|
| **BYO Key** | $19/mo | Engineers, privacy nerds with their own Claude/OpenAI keys | Once 20+ have asked |
| **Wira** (current) | $29/mo or $290/yr | Solo operators | Now |
| **Wira Pro** | $79/mo | High-volume users wanting voice notes, multi-number, priority brain | After 50 paying users |
| **Wira Business** | $200+/mo | Small teams with shared inbox | When asked, not before |

---

**Sources:**
- [Anthropic API pricing](https://www.anthropic.com/api)
- [Claude Sonnet 4.6 token pricing breakdown](https://pricepertoken.com/pricing-page/model/anthropic-claude-sonnet-4.6)
- [Martin AI pricing](https://www.trymartin.com/pricing)
- [Wati vs AiSensy 2026 comparison](https://aisensy.com/aisensy-vs-wati)
- [WhatsApp AI chatbot pricing roundup 2026](https://www.kommunicate.io/blog/best-whatsapp-ai-chatbots/)
- [Meta WhatsApp Writing Help (TechCrunch, Mar 2026)](https://techcrunch.com/2026/03/26/whatsapp-can-now-draft-ai-generated-responses-based-on-your-conversations/)
