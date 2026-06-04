import Footer from "@/components/Footer";
import Nav from "@/components/Nav";
import { PRODUCT } from "@/lib/brand";

/**
 * Plain-language explainer page. Deliberately NOT a sales page — it lives off
 * the home flow so anyone curious can learn what an agent actually is, what
 * skills and tools mean, and how the free/local path gets them going fast.
 */
export default function Learn() {
  return (
    <>
      <Nav />
      <main className="container-narrow py-16 prose-spacing">
        <p className="text-sm font-semibold text-accent">Plain-language guide</p>
        <h1 className="mt-2 text-5xl">What {PRODUCT.name} actually is</h1>
        <p className="mt-3 text-lg text-ink-muted">
          No jargon. If you've heard the words "agent," "agency," "skills," and
          "tools" thrown around and weren't sure what they meant, this page is
          for you.
        </p>

        <Block title={`What ${PRODUCT.name} is`}>
          <p>
            {PRODUCT.name} is a personal assistant that lives on your own
            computer. You talk to it on WhatsApp — the same app you already use
            all day — and it does real work for you: summarizing things, finding
            files, drafting replies, making plans.
          </p>
          <p>
            The key difference from a normal chatbot: it runs on{" "}
            <b>your machine</b>, under <b>your control</b>, and it can actually{" "}
            <i>do</i> things, not just talk about them.
          </p>
        </Block>

        <Block title="What an agent is">
          <p>
            A chatbot answers questions. An <b>agent</b> takes action. Give an
            agent a goal — "find my latest invoice and tell me what's owed" — and
            it figures out the steps, uses the tools it has, and comes back with
            the result.
          </p>
          <p>
            Think of the difference between asking a friend "how do I find this
            file?" versus asking them "can you find this file for me?" The second
            one is an agent.
          </p>
        </Block>

        <Block title="What an agency is">
          <p>
            One agent is helpful. An <b>agency</b> is a team of them working
            together — like a small company of specialists. One agent might be
            good at research, another at writing, another at organizing files.
            They hand work to each other to finish a bigger job.
          </p>
          <p>
            {PRODUCT.name} starts you with one simple agent on day one. As you
            grow, it can introduce more of this team-of-agents power — without
            forcing you to learn all of it up front.
          </p>
        </Block>

        <Block title="What skills are">
          <p>
            A <b>skill</b> is something an agent has learned how to do well — a
            reusable recipe. "Draft a polite reply," "summarize a long document,"
            "make a shipping plan." Skills are the know-how.
          </p>
          <p>
            Over time an agent can pick up more skills, the same way a new
            employee gets better at their job the longer they're around.
          </p>
        </Block>

        <Block title="What tools are">
          <p>
            <b>Tools</b> are what an agent is allowed to touch to get work done —
            reading a file, searching the web, checking your calendar. Skills are
            the know-how; tools are the hands.
          </p>
          <p>
            You stay in charge of which tools {PRODUCT.name} can use.{" "}
            {PRODUCT.name} is owner-controlled by default and pauses to ask before
            anything risky — spending money, deleting things, or sending
            something public.
          </p>
        </Block>

        <Block title="The brain — and the fastest free way in">
          <p>
            Every agent needs a "brain" — the AI model that does the thinking.{" "}
            {PRODUCT.name} lets you choose, and you can switch any time:
          </p>
          <ul>
            <li>
              <b>Local model (free &amp; private)</b> — {PRODUCT.name} installs an
              open model that runs entirely on your Mac. Nothing leaves your
              computer, and there's nothing to pay. One quick install and you're
              going. Best if privacy matters to you.
            </li>
            <li>
              <b>A low-cost API key (best value)</b> — paste a key from a provider
              like Groq or DeepSeek. Their free and cheap tiers give you a fast
              cloud brain in seconds, with no monthly subscription. {PRODUCT.name}{" "}
              tests the key before saving it.
            </li>
            <li>
              <b>Your ChatGPT subscription</b> — already pay for ChatGPT? Connect
              it and use the brain you've got.
            </li>
          </ul>
          <p>
            The local model and the free provider tiers mean you can be up and
            running for <b>$0</b> — no subscription, no waiting.
          </p>
        </Block>

        <Block title="Ready to try it?">
          <p>
            Download {PRODUCT.name}, pick a brain in one screen, scan a WhatsApp
            code, and send your first message.
          </p>
          <div className="not-prose mt-4 flex flex-wrap gap-3">
            <a href="/onboarding" className="btn-primary">
              Start setup
            </a>
            <a href="/#pricing" className="btn-ghost">
              See pricing
            </a>
          </div>
        </Block>
      </main>
      <Footer />
    </>
  );
}

function Block({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="mt-10">
      <h2 className="text-2xl mb-3">{title}</h2>
      <div className="text-ink-muted space-y-3 [&_ul]:list-disc [&_ul]:pl-6 [&_ul]:space-y-2">
        {children}
      </div>
    </section>
  );
}
