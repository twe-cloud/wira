/**
 * Brand single source of truth.
 *
 * When the name agent returns, update PRODUCT here and every page picks it up.
 * Same for prices: the Pricing component reads from PRICING below.
 */

export const PRODUCT = {
  name: "Wira",
  parentBrand: "Motwe",
  domain: "wira.io",
  tagline: "Your WhatsApp, finally answered.",
  hook: "Your WhatsApp keeps replying. You don't have to.",
  description:
    "Wira is an AI assistant that lives on your personal WhatsApp number. Answers in your voice, remembers every contact, and only pings you for what actually needs you.",
  supportEmail: "hello@wira.io",
  city: "Nairobi",
};

/**
 * Pricing: $29/month or $290/year (save 2 months). Single tier per UX brief
 * — three-column pricing screams "which one is the trap" for this audience.
 *
 * Anchoring: closest competitor Martin AI is $21–30/mo. Wati's B2B platform
 * is $39–99/mo + WhatsApp fees. Claude Sonnet 4.6 token cost at ~200 replies/
 * day with prompt caching = ~$5–12/mo COGS, leaving healthy margin at $29.
 */
export const PRICING = {
  monthly: { price: 29, label: "$29", per: "/month" },
  annual: { price: 290, label: "$290", per: "/year", saveLabel: "Save $58" },
  // Set these once you've created the recurring Prices in Stripe dashboard
  stripePriceMonthly: "price_REPLACE_MONTHLY",
  stripePriceAnnual: "price_REPLACE_ANNUAL",
  includes: [
    "Lives on your personal WhatsApp number (QR pair)",
    "Per-contact memory — never forgets who someone is",
    "Drafts first, auto-sends when you trust it",
    "Claude or GPT brain — or fully local via Ollama",
    "Voice-trained from your past replies",
    "Cancel anytime, no setup fee",
  ],
};

export const PILLARS = [
  {
    name: "Sounds Like You",
    body:
      "Pair once via QR, paste a few past chats, and it mirrors your phrasing, your emojis, your “lol noted” — not a corporate “Thank you for reaching out.”",
  },
  {
    name: "Remembers Everyone",
    body:
      "Per-contact memory: who they are, what you're owed, what you promised last Tuesday — so nobody gets a cold reply twice.",
  },
  {
    name: "Knows When to Tap You",
    body:
      "Routes the 5% that actually need a decision — pricing, scope changes, anything emotional — to a private summary, with a one-tap “send it” reply.",
  },
];

export const FAQS = [
  {
    q: "Will WhatsApp ban my number?",
    a: "We pair via WhatsApp's multi-device protocol — the same one WhatsApp Web uses. We don't send unsolicited messages, we rate-limit like a human, and you choose exactly who gets replies. Same risk profile as leaving WhatsApp Web open.",
  },
  {
    q: "What if it says something stupid to a client?",
    a: "By default, it drafts a reply and pings you to approve in one tap — it only auto-sends to contacts you whitelist. Escalation is the default, not the exception.",
  },
  {
    q: "Isn't it weird to have an AI reply as me?",
    a: "It's not impersonation — it's an assistant replying for you, the same way an EA drafts emails. You set the line on what it can answer alone, and it always tells people it's an AI if they ask.",
  },
  {
    q: "Why not just use ChatGPT?",
    a: "ChatGPT doesn't know your contacts, doesn't live on your number, and won't reply at 2am while you sleep. Wira does — right inside the app you already use.",
  },
  {
    q: "WhatsApp has built-in AI writing help now. Isn't this the same?",
    a: "No. Meta's Writing Help drafts a single suggestion for you to send manually. Wira is autonomous — it learns your voice from your real past chats, remembers each contact across weeks, and can reply for you while your phone's in your pocket. Different category, same surface.",
  },
  {
    q: "What about privacy?",
    a: "Pick your brain: Claude (encrypted in transit, never trained on your data) or Ollama running on your own machine (your chats never leave your laptop). You can choose per contact, and you can delete everything at any time.",
  },
  {
    q: "Does it read all my messages?",
    a: "Only the chats you turn on. Groups are off by default. You can whitelist or blacklist contacts at any moment, and there's a global pause that stops everything in one tap.",
  },
];
