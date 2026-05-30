import Footer from "@/components/Footer";
import Nav from "@/components/Nav";
import { PRODUCT } from "@/lib/brand";

/**
 * REVIEW BEFORE PUBLISHING. Starting template — not legal advice.
 * Have counsel adapt to your jurisdiction and risk profile.
 */
export default function Terms() {
  return (
    <>
      <Nav />
      <main className="container-narrow py-16">
        <h1 className="text-5xl">Terms of Service</h1>
        <p className="mt-2 text-ink-muted">
          Last updated: {new Date().toISOString().slice(0, 10)}
        </p>

        <Block title="Plain English summary">
          <p>
            Pay your subscription. Use {PRODUCT.name} for your own communication.
            Don't use it to spam or harass anyone. If something goes wrong,
            we'll do our best to fix it but our liability is capped at what
            you paid us in the last 12 months.
          </p>
        </Block>

        <Block title="1. The Service">
          <p>
            {PRODUCT.name} ("the Service") connects to your personal WhatsApp
            via WhatsApp's multi-device protocol and replies to messages on
            your behalf using AI. We are not affiliated with WhatsApp or Meta.
          </p>
        </Block>

        <Block title="2. Your account">
          <p>
            You're responsible for keeping your login secure and for everything
            done with your account. Tell us within 7 days if it's compromised.
          </p>
        </Block>

        <Block title="3. Acceptable use">
          <p>You agree not to:</p>
          <ul>
            <li>Send spam, unsolicited bulk messages, or marketing to people who haven't opted in.</li>
            <li>Harass, deceive, defraud, or harm anyone.</li>
            <li>Impersonate someone else without their permission.</li>
            <li>Use the Service to break any law applicable to you or the recipient.</li>
            <li>Attempt to reverse-engineer, resell, or sublicense the Service.</li>
          </ul>
          <p>
            We can suspend or terminate accounts that breach this section, with
            or without notice.
          </p>
        </Block>

        <Block title="4. WhatsApp">
          <p>
            WhatsApp is a third-party service with its own terms. Their rules
            apply to your number, not us. If WhatsApp restricts your number,
            we cannot reverse that. We rate-limit replies and recommend
            against bulk outreach for exactly this reason.
          </p>
        </Block>

        <Block title="5. Payments">
          <p>
            Subscriptions renew automatically. Cancel from your dashboard at
            any time; access continues until the end of the current billing
            period. We don't issue refunds for partial months but will review
            edge cases on request.
          </p>
        </Block>

        <Block title="6. AI output">
          <p>
            {PRODUCT.name} generates replies using AI models. Output may be
            inaccurate, inappropriate, or unexpected. You are responsible for
            what is sent from your account. We recommend keeping approval mode
            on until you trust the replies.
          </p>
        </Block>

        <Block title="7. Intellectual property">
          <p>
            We own the software. You own your messages, your account data, and
            anything you create using the Service. You grant us a limited
            licence to process your messages to provide the Service.
          </p>
        </Block>

        <Block title="8. Warranty disclaimer">
          <p>
            The Service is provided "as is" without warranties of any kind. We
            don't guarantee it will be uninterrupted, error-free, or fit for
            any particular purpose.
          </p>
        </Block>

        <Block title="9. Limitation of liability">
          <p>
            To the maximum extent allowed by law, our total liability for any
            claim is capped at the amount you paid us in the 12 months before
            the claim arose. We're not liable for indirect, incidental, or
            consequential damages.
          </p>
        </Block>

        <Block title="10. Governing law">
          <p>
            These Terms are governed by the laws of Kenya. Any dispute will be
            resolved by the courts of Nairobi unless your local consumer law
            says otherwise.
          </p>
        </Block>

        <Block title="11. Changes">
          <p>
            We may update these Terms. Material changes are emailed to active
            customers 30 days before they take effect.
          </p>
        </Block>

        <Block title="12. Contact">
          <p>
            Questions:{" "}
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
