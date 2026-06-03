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
  tagline: "Your first personal agent, reached from WhatsApp.",
  hook: "A real local agent on your computer. Your phone is just the fastest way in.",
  description:
    "Wira is a branded path into a real Hermes agent that lives on your computer, is reached from WhatsApp, and grows with you from simple phone-first commands into deeper agentic work.",
  supportEmail: "hello@wira.io",
  city: "Nairobi",
};

/**
 * Pricing: early positioning should sell the branded local-agent path, not a text-reply bot.
 */
export const PRICING = {
  local: { price: 49, label: "$49", per: "one-time" },
  // Live Wira Local one-time setup price in the Ni Biashara Stripe account.
  stripePriceLocal: "price_1TcrAXRVrXHv0YFpfmw35hIw",
  includes: [
    "One-time Wira Local purchase — no monthly fee for the local install",
    "Lives on your own computer — not trapped in a browser tab",
    "Reach Wira from WhatsApp with a QR-paired setup",
    "Private owner/operator control surface by default",
    "ChatGPT, Claude, GPT, or local-model brain options",
    "A guided path into Hermes Desktop and CLI when you're ready",
  ],
};

export const PILLARS = [
  {
    name: "Starts Simple",
    body:
      "You begin from the one place you already use all day: your phone. Wira handles pairing, setup, and the scary parts so your first real agent doesn't feel like infrastructure.",
  },
  {
    name: "Lives On Your Machine",
    body:
      "The goal is not another hosted chat toy. Wira is the branded surface for a real local agent on your own computer, with the files, tools, and context you choose to unlock.",
  },
  {
    name: "Grows Into Hermes",
    body:
      "You don't need to know about skills, tools, or CLI on day one. But when you're ready, Wira should open the door to the deeper Hermes surfaces instead of trapping you in a simplified shell forever.",
  },
];

export const FAQS = [
  {
    q: "Is this just a WhatsApp bot?",
    a: "No. WhatsApp is the control surface, not the product. Wira is a branded path into a real local agent that lives on your computer and is meant to grow with you.",
  },
  {
    q: "Why not just use ChatGPT?",
    a: "Because ChatGPT is still mostly a chat destination. Wira is the bridge into agentic work on your own machine — and it starts from your phone instead of making you learn the whole stack up front.",
  },
  {
    q: "What does Wira do?",
    a: "Wira is both the product and the name you talk to on day one. It keeps the first experience simple: WhatsApp on your phone, a local agent on your computer, and a deeper Hermes path when you're ready.",
  },
  {
    q: "Will I be able to use Hermes directly later?",
    a: "Yes. That's part of the thesis. Wira should make Hermes Desktop and CLI discoverable organically once you're ready, instead of dropping all the agent jargon on you at the start.",
  },
  {
    q: "What about privacy?",
    a: "The Local path is meant to run on your own machine with deliberate permissions. The goal is owner control: you choose what files, tools, browser actions, and automations the agent is allowed to touch.",
  },
  {
    q: "Can other people talk to my agent?",
    a: "Not by default. The intended Local and Business default is owner lock: this is your private operator surface first, not a public auto-reply product.",
  },
];
