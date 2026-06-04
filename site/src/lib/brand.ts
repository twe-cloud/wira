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
    "Wira sets up a personal agent on your computer, runs it on a private local model or the ChatGPT subscription you already have, and lets you talk to it on WhatsApp.",
  supportEmail: "hello@wira.io",
  city: "Nairobi",
  // Direct download for the signed + notarized macOS app (GitHub Release asset).
  downloadMacUrl:
    "https://github.com/twe-cloud/wira/releases/latest/download/Wira.dmg",
  // The app is an Apple Silicon (arm64) build — it will not launch on Intel Macs.
  // Browser JS can't reliably tell the two apart, so we state the requirement.
  systemRequirement: "Requires an Apple Silicon Mac (M1 or newer), macOS 12+.",
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
    "Run it fully private on your Mac, or use the ChatGPT subscription you already have",
    "Grows into deeper local agent work when you're ready",
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
      "The goal is not another hosted chat toy. Wira is the branded surface for a real local agent on your own computer, with the local access you choose to unlock.",
  },
  {
    name: "Grows Into Hermes",
    body:
      "You don't need to learn the deeper system on day one. Start with ChatGPT and WhatsApp; Wira can introduce more power later instead of trapping you in a simplified shell forever.",
  },
];

export const FAQS = [
  {
    q: "Is this just a WhatsApp bot?",
    a: "No. WhatsApp is the control surface, not the product. Wira is a branded path into a real local agent that lives on your computer and is meant to grow with you.",
  },
  {
    q: "Why not just use ChatGPT?",
    a: "Because ChatGPT is still mostly a place you go to chat. Wira connects that subscription to an agent on your own computer and lets you reach it from your phone.",
  },
  {
    q: "What does Wira do?",
    a: "Wira is both the product and the name you talk to on day one. It keeps the first experience simple: WhatsApp on your phone, ChatGPT connected, and a local agent on your computer.",
  },
  {
    q: "Can it grow beyond the starter flow?",
    a: "Yes. Wira starts simple on purpose, then can introduce deeper local-agent surfaces once you are ready.",
  },
  {
    q: "What about privacy?",
    a: "The Local path is meant to run on your own machine with deliberate permissions. The goal is owner control: you choose what the agent is allowed to access and when it must ask first.",
  },
  {
    q: "Can it run without ChatGPT?",
    a: "Yes. During setup Wira can install a private local model that runs entirely on your Mac — free to run, with nothing leaving your computer. Prefer the brain you already pay for? Connect your ChatGPT subscription instead. You can switch later.",
  },
  {
    q: "Can other people talk to my agent?",
    a: "Not by default. The intended Local and Business default is owner lock: this is your private operator surface first, not a public auto-reply product.",
  },
];
