/**
 * Brand single source of truth.
 *
 * When the name agent returns, update PRODUCT here and every page picks it up.
 * Same for prices: the Pricing component reads from PRICING below.
 */

const DOWNLOAD_BASE = (import.meta.env.VITE_WIRA_DOWNLOAD_BASE || "").replace(/\/$/, "");
const macDownloadPath = "/download/wira-mac";
const windowsDownloadPath = "/download/wira-windows";

export const PRODUCT = {
  name: "Wira",
  parentBrand: "Motwe",
  domain: "wira.io",
  tagline: "Your first personal agent, reached from WhatsApp.",
  hook: "A real local agent on your computer. Your phone is just the fastest way in.",
  description:
    "Wira sets up a personal agent on your computer, connects it to a free or paid brain of your choice, and lets you talk to it on WhatsApp.",
  supportEmail: "hello@wira.io",
  city: "Dallas, TX",
  // Stable product-controlled download route fronted by the Cloudflare Worker.
  // Keep this same-origin when the official product domain fronts it; otherwise
  // point to the Worker explicitly for embedded copies like nibiashara.biz/wira.
  downloadMacUrl: DOWNLOAD_BASE ? `${DOWNLOAD_BASE}${macDownloadPath}` : macDownloadPath,
  downloadWindowsUrl: DOWNLOAD_BASE ? `${DOWNLOAD_BASE}${windowsDownloadPath}` : windowsDownloadPath,
  systemRequirement: "Mac and Windows downloads are available now. Apple Silicon is the best fit for fully private local AI; Intel Macs and Windows PCs start fastest on the free or ChatGPT brain.",
  heroSupportLine: "Pair via QR code · Mac download live · Windows download in early beta · start free or connect ChatGPT.",
  pricingSupportLine: "Secure checkout by Stripe · one-time payment · works on Mac and Windows · no local monthly fee.",
  windowsBetaNote: "The Windows app is an early beta and isn't code-signed yet, so Windows may show a SmartScreen warning — choose More info, then Run anyway to install.",
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
    "Start free in seconds, use the ChatGPT subscription you already have, or keep the brain private when your machine is a good fit",
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
      "You don't need to learn the deeper system on day one. Start with the fastest free brain or the ChatGPT subscription you already have, then let Wira introduce more power later instead of trapping you in a simplified shell forever.",
  },
];

export const AGENT_PROMISES = [
  {
    name: "It remembers the stuff you usually have to repeat",
    body:
      "Preferences, recurring contacts, familiar tasks, the way you like something phrased — Wira can keep more of that context in play instead of making every session a fresh start.",
  },
  {
    name: "It shortens the path from request to result",
    body:
      "What starts as a long explanation can become a quick instruction. The more often you use it, the less setup each familiar task needs.",
  },
  {
    name: "It works against your actual digital life",
    body:
      "The WhatsApp thread is just the entry point. The real advantage is that the agent can help around your files, notes, drafts, reminders, and the tools you already use.",
  },
  {
    name: "It starts light, then earns a bigger role",
    body:
      "You can begin with simple asks. Over time Wira can help prep, organize, summarize, and handle more of the small but constant work around your day.",
  },
];

export const AGENT_PULLS = [
  "Less re-explaining.",
  "Faster handoffs on familiar tasks.",
  "A WhatsApp thread that becomes a real working tool.",
  "A simple start that can grow into deeper Hermes power later.",
];

export const FAQS = [
  {
    q: "Is this just a WhatsApp bot?",
    a: "No. WhatsApp is the control surface, not the product. Wira is a branded path into a real local agent that lives on your computer and is meant to grow with you.",
  },
  {
    q: "Why not just use ChatGPT?",
    a: "Because ChatGPT is still mostly a place you go to chat. Wira turns that into a real agent on your own computer, reachable from your phone — and if you want to start free instead, you can.",
  },
  {
    q: "What does Wira do?",
    a: "Wira is both the product and the name you talk to on day one. It keeps the first experience simple: WhatsApp on your phone, a brain you choose, and a local agent on your computer.",
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
    a: "Yes. The fastest free option is to sign up with a service like Groq or DeepSeek and paste the key Wira asks for — free tiers get you running in seconds. You can also connect the ChatGPT subscription you already have, or keep the brain private when your machine is a good fit. You can switch any time.",
  },
  {
    q: "What's the fastest way to get going?",
    a: "Sign up free with a service like Groq or DeepSeek, paste the key Wira asks for, and you are chatting in under a minute — no subscription needed. Or connect the ChatGPT subscription you already have. Both paths work right away.",
  },
  {
    q: "Can other people talk to my agent?",
    a: "Not by default. The intended Local and Business default is owner lock: this is your private operator surface first, not a public auto-reply product.",
  },
  {
    q: "What is actually cool about having Wira on WhatsApp?",
    a: "It means your agent is reachable from the one place you already check all day, while the real value keeps building underneath: more memory, better context, smoother repeated tasks, and a cleaner path from simple requests into real operator help.",
  },
];
