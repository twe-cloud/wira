import Footer from "@/components/Footer";
import Nav from "@/components/Nav";
import { PRODUCT } from "@/lib/brand";

/**
 * REVIEW BEFORE PUBLISHING. This is a reasonable starting template — not
 * legal advice. Run by counsel familiar with your jurisdiction (GDPR for EU
 * users, CCPA for California, Kenya Data Protection Act).
 *
 * Describes Wira Local (the product sold here): a self-hosted agent that runs
 * on the buyer's own computer. Managed "Wira Business" deployments are covered
 * by a separate agreement.
 */
export default function Privacy() {
  return (
    <>
      <Nav />
      <main className="container-narrow py-16 prose-spacing">
        <h1 className="text-5xl">Privacy</h1>
        <p className="mt-2 text-ink-muted">Last updated: 2026-06-10</p>

        <Block title="In one paragraph">
          <p>
            {PRODUCT.name} runs on your own computer — not our servers. Your
            WhatsApp messages, the agent's memory, and your login tokens stay on
            your machine in a private folder (<code>~/.wira</code>) with
            locked-down file permissions. The only thing we receive is your
            purchase, handled by Stripe. We can't read your conversations,
            because we never have them.
          </p>
        </Block>

        <Block title="What stays on your computer">
          <ul>
            <li>
              <b>WhatsApp pairing token</b> — the same kind of linked-device
              token WhatsApp Web uses, so {PRODUCT.name} can reach your number.
            </li>
            <li>
              <b>Conversations &amp; memory</b> — your messages, the replies, and
              per-contact notes, in a local database on your machine.
            </li>
            <li>
              <b>Your brain choice &amp; any API key you paste</b> — written to a
              local, permission-restricted file (readable only by your user
              account). None of this folder is sent to us.
            </li>
          </ul>
        </Block>

        <Block title="What leaves your computer">
          <ul>
            <li>
              <b>Message text → the AI brain you pick.</b> If you choose ChatGPT
              or a hosted provider (Groq, DeepSeek, OpenRouter, Gemini, and the
              like), your message text goes to that provider under their terms.
              If you pick a <b>local brain</b> (Ollama / LM Studio), nothing
              leaves your machine at all.
            </li>
            <li>
              <b>Purchase → Stripe.</b> Stripe handles checkout; we see your
              email and that you paid — never your card number.
            </li>
          </ul>
        </Block>

        <Block title="What we (the makers) collect">
          <ul>
            <li>
              Your <b>purchase record</b> via Stripe, and standard{" "}
              <b>web-server logs</b> for this website via Cloudflare. That's it.
            </li>
            <li>
              We do <b>not</b> host, store, or back up your conversations, and
              there is no account dashboard holding your chats — that data lives
              on your computer.
            </li>
          </ul>
        </Block>

        <Block title="Third-party brains">
          <p>
            Each AI provider you connect has its own privacy policy and data
            terms — review the one you choose (for example OpenAI, Anthropic,
            Google, or Groq). Want zero third parties in the loop? Use the local
            brain, and your messages never leave your machine.
          </p>
        </Block>

        <Block title="Deleting your data">
          <p>
            Because it lives on your machine, you're in control: delete the{" "}
            <code>~/.wira</code> folder (or uninstall {PRODUCT.name}) and your
            tokens, memory, and conversations are gone. There's no server copy to
            request — we don't have one.
          </p>
        </Block>

        <Block title="Security">
          <p>
            Tokens and config are written with restricted file permissions on
            your machine, never in plaintext logs. This website is served over
            TLS with HSTS, and payments are handled entirely by Stripe.
          </p>
        </Block>

        <Block title="Children">
          <p>
            {PRODUCT.name} is not for under-16s. We don't knowingly collect data
            from minors.
          </p>
        </Block>

        <Block title="Changes">
          <p>
            If we materially change how data is handled, we'll update the date at
            the top of this page.
          </p>
        </Block>

        <Block title="Contact">
          <p>
            <a className="text-accent" href={`mailto:${PRODUCT.supportEmail}`}>
              {PRODUCT.supportEmail}
            </a>
          </p>
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
