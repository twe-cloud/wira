import Footer from "@/components/Footer";
import Nav from "@/components/Nav";
import { PRODUCT } from "@/lib/brand";

/**
 * REVIEW BEFORE PUBLISHING. This is a reasonable starting template — not
 * legal advice. Run by counsel familiar with your jurisdiction (Kenya
 * Data Protection Act, GDPR for EU users, CCPA for California).
 */
export default function Privacy() {
  return (
    <>
      <Nav />
      <main className="container-narrow py-16 prose-spacing">
        <h1 className="text-5xl">Privacy</h1>
        <p className="mt-2 text-ink-muted">
          Last updated: {new Date().toISOString().slice(0, 10)}
        </p>

        <Block title="In one paragraph">
          <p>
            {PRODUCT.name} processes your WhatsApp messages so an AI can reply
            on your behalf. We store the minimum needed to do that, never sell
            your data, and let you delete everything at any time. Below is the
            detail.
          </p>
        </Block>

        <Block title="What we collect">
          <ul>
            <li>
              <b>Account info</b> — email, name, billing info (handled by
              Stripe; we never see your card number).
            </li>
            <li>
              <b>WhatsApp session</b> — an encrypted device pairing token that
              keeps {PRODUCT.name} linked to your number. Same kind of token
              WhatsApp Web uses.
            </li>
            <li>
              <b>Conversations</b> — incoming WhatsApp messages and the replies
              we generate, plus per-contact memory ("who is this person").
              Stored encrypted at rest.
            </li>
            <li>
              <b>Usage metrics</b> — how many messages handled, response
              times, error counts. Used to improve the product.
            </li>
          </ul>
        </Block>

        <Block title="What we don't collect">
          <ul>
            <li>WhatsApp media (images, voice notes, documents) unless you turn that on.</li>
            <li>Anything from chats you've turned off or excluded.</li>
            <li>Your contacts' phone numbers beyond what we need to thread their messages.</li>
          </ul>
        </Block>

        <Block title="Where it goes">
          <ul>
            <li>
              <b>Anthropic (Claude)</b> — message text is sent to Claude to
              generate a reply. Per Anthropic's policy, your data is not used
              to train their models.
            </li>
            <li>
              <b>Local mode (Ollama)</b> — if you choose the local brain,
              messages never leave the machine you run {PRODUCT.name} on. We
              still store account + billing data on our servers.
            </li>
            <li>
              <b>Stripe</b> — payments only.
            </li>
            <li>
              <b>Netlify</b> — hosts this website. Standard server logs.
            </li>
            <li>We don't share, sell, or rent your data to anyone else.</li>
          </ul>
        </Block>

        <Block title="How long we keep it">
          <ul>
            <li>Conversations: as long as your account is active. Delete any time.</li>
            <li>Billing records: 7 years (tax requirement).</li>
            <li>Backups: rolling 30 days, then permanently deleted.</li>
          </ul>
        </Block>

        <Block title="Your rights">
          <p>
            You can export, correct, or delete all your data from the dashboard.
            Under GDPR (EU/UK), Kenya's Data Protection Act 2019, and CCPA
            (California), you can also request a copy of everything we hold on
            you. Email{" "}
            <a className="text-accent" href={`mailto:${PRODUCT.supportEmail}`}>
              {PRODUCT.supportEmail}
            </a>{" "}
            and we'll respond within 30 days.
          </p>
        </Block>

        <Block title="Security">
          <p>
            TLS everywhere, AES-256 at rest, no plaintext secrets in logs, and
            no one on the team can read your conversations without a support
            request from you that grants temporary access.
          </p>
        </Block>

        <Block title="Children">
          <p>
            {PRODUCT.name} is not for under-16s. We don't knowingly collect
            data from minors.
          </p>
        </Block>

        <Block title="Changes">
          <p>
            If we materially change how we handle your data, we email you and
            update the date at the top of this page.
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
