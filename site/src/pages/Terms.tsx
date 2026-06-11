import Footer from "@/components/Footer";
import Nav from "@/components/Nav";
import { PRODUCT } from "@/lib/brand";

export default function Terms() {
  return (
    <>
      <Nav />
      <main className="container-narrow py-16">
        <h1 className="text-5xl">Wira Local Terms</h1>
        <p className="mt-2 text-ink-muted">Last updated: 2026-06-03</p>

        <Block title="Plain summary">
          <p>
            {PRODUCT.name} Local is an enablement setup for your own machine,
            WhatsApp account, tools, and model/provider accounts. After setup,
            your agent is yours to run.
          </p>
        </Block>

        <Block title="Refunds">
          <p>
            All sales are final. {PRODUCT.name} Local is a one-time digital
            purchase you download and run on your own machine, so we do not
            offer refunds once purchased. If {PRODUCT.name} will not run for
            you, email{" "}
            <a className="text-accent" href={`mailto:${PRODUCT.supportEmail}`}>
              {PRODUCT.supportEmail}
            </a>{" "}
            and we will help you get it working.
          </p>
        </Block>

        <Block title="1. What Wira Local provides">
          <p>
            {PRODUCT.name} Local provides the app/download, setup instructions,
            and a way to connect a supported brain and WhatsApp linked-device
            session. It is not a managed hosted service.
          </p>
        </Block>

        <Block title="2. Your responsibility">
          <p>
            You control your machine, WhatsApp number, ChatGPT/API/local-model
            account, tools, data, backups, updates, reply mode, and messages.
            You are responsible for what your agent sends or does after setup.
          </p>
        </Block>

        <Block title="3. Acceptable use">
          <p>You agree not to:</p>
          <ul>
            <li>Send spam, unsolicited bulk messages, or marketing to people who haven't opted in.</li>
            <li>Harass, deceive, defraud, or harm anyone.</li>
            <li>Impersonate someone else without their permission.</li>
            <li>Use the Service to break any law applicable to you or the recipient.</li>
            <li>Give Wira destructive system access unless you accept that risk.</li>
          </ul>
        </Block>

        <Block title="4. WhatsApp connection (unofficial — please read)">
          <p>
            WhatsApp is a third-party service with its own terms, and{" "}
            {PRODUCT.name} is not built, endorsed, or supported by WhatsApp or
            Meta. {PRODUCT.name} connects through an unofficial linked-device
            client that works with WhatsApp's Linked Devices protocol without
            being an official WhatsApp product. Using it may violate WhatsApp's
            Terms of Service, and your number could be temporarily or
            permanently restricted or banned.
          </p>
          <p>
            We strongly recommend pairing a secondary number you are comfortable
            risking. If WhatsApp or Meta restricts your number, Ni Biashara
            cannot reverse that and is not responsible for it.
          </p>
        </Block>

        <Block title="5. Not managed support">
          <p>
            Wira Local does not include hosted uptime, monitoring, account
            administration, tool administration, data recovery, managed backups,
            or hands-on support after handoff unless a separate written service
            is sold.
          </p>
        </Block>

        <Block title="6. AI output">
          <p>
            {PRODUCT.name} generates replies using AI models. Output may be
            inaccurate, inappropriate, or unexpected. You are responsible for
            what is sent from your account and for any actions taken through
            tools you connect. Keep draft mode on until you trust the replies.
          </p>
        </Block>

        <Block title="7. Updates">
          <p>
            Updates are manual. Wira can open the latest release page, and you
            can download and install a newer build. Local settings, auth,
            WhatsApp session, memory, drafts, and onboarding state are kept in
            your local Wira folder (<code>~/.wira</code>).
          </p>
        </Block>

        <Block title="8. Warranty disclaimer">
          <p>
            Wira Local is provided "as is" without warranties of any kind. We do
            not guarantee uninterrupted operation, error-free output, account
            safety, or fitness for a particular purpose.
          </p>
        </Block>

        <Block title="9. Limitation of liability">
          <p>
            To the maximum extent allowed by law, Ni Biashara is not responsible
            for lost messages, account restrictions, bad replies, deleted files,
            broken local systems, third-party provider failures, business losses,
            customer disputes, or actions taken by your agent after setup.
          </p>
        </Block>

        <Block title="10. Governing law">
          <p>
            These terms are governed by the law that applies to Ni Biashara LLC
            and the transaction, unless mandatory consumer law says otherwise.
          </p>
        </Block>

        <Block title="11. Changes">
          <p>
            We may update these terms. The version shown at checkout or setup is
            the version attached to that purchase unless a later written service
            agreement replaces it.
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
