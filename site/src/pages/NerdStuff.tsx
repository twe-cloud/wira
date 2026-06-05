import Footer from "@/components/Footer";
import Nav from "@/components/Nav";
import { PRODUCT } from "@/lib/brand";
import { Link } from "react-router-dom";

export default function NerdStuff() {
  return (
    <>
      <Nav />
      <main className="container-narrow py-16 prose-spacing">
        <p className="text-sm font-semibold text-accent">For the ones who like opening the back panel</p>
        <h1 className="mt-2 text-5xl">Nerd stuff</h1>
        <p className="mt-3 text-lg text-ink-muted">
          {PRODUCT.name} stays simple on purpose: message your agent on WhatsApp
          and get real work done. Under that surface is a local agent on your own
          machine. If that already sounds normal to you, welcome.
        </p>

        <Block title={`What ${PRODUCT.name} actually installs`}>
          <ul>
            <li>A desktop app and local runtime on your own machine.</li>
            <li>A private Wira data folder at <code>~/.wira</code>.</li>
            <li>A WhatsApp linked-device connection that you control.</li>
            <li>Your chosen AI brain: free tier, ChatGPT, or a private local model.</li>
            <li>Local helper scripts and configuration files needed to run it.</li>
          </ul>
          <p>
            The important point: the useful part is not a hosted web chat. The
            useful part is the agent living on your computer.
          </p>
        </Block>

        <Block title="The honest handoff">
          <p>
            Wira is the easier front door. The deeper runtime underneath is
            Hermes Agent. We do not bury that; we just do not lead with it for
            everyone on day one.
          </p>
          <p>
            If all you want is “talk to my agent on WhatsApp,” that is enough. If
            you later want terminal control, more tools, richer automation, or a
            wider command surface, the deeper path is already there.
          </p>
        </Block>

        <Block title="What we can share publicly">
          <p>
            Transparency matters, so here is the public-safe version of the local
            flow. No passwords, API keys, webhook secrets, QR sessions, or private
            customer config are shown here.
          </p>
          <Code>
{`# inside the project folder
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env
.venv/bin/python setup.py`}
          </Code>
          <p>
            That setup path creates the local environment, prepares the config,
            and opens the guided setup so you can pick a brain and pair WhatsApp.
          </p>
        </Block>

        <Block title="What the install script does">
          <ol>
            <li>Checks that Python is installed and recent enough.</li>
            <li>Creates a virtual environment for the runtime.</li>
            <li>Installs the required Python packages.</li>
            <li>Creates a local <code>.env</code> file from a template if needed.</li>
            <li>Hands off to guided setup so you can choose your model and scan the WhatsApp QR code.</li>
          </ol>
          <p>
            That means technical buyers can see the shape of the install without
            us pretending there is magic involved, while everyone else can simply
            buy the done-for-you setup and skip the plumbing.
          </p>
        </Block>

        <Block title="Update without panic">
          <p>
            Local settings, WhatsApp pairing, memory, drafts, and onboarding state
            live in <code>~/.wira</code>, not inside the app bundle itself.
          </p>
          <ul>
            <li>Open Wira and use <b>Check for Updates</b> when available.</li>
            <li>Or download the latest release and replace the app.</li>
            <li>Your local Wira folder should remain in place.</li>
            <li>If WhatsApp says the linked-device session expired, just scan a fresh QR code.</li>
          </ul>
          <p>
            For most people, updating should feel like replacing an app, not like
            rebuilding a whole system from scratch.
          </p>
        </Block>

        <Block title="Reinstall if something gets weird">
          <ol>
            <li>Quit the app.</li>
            <li>Install a fresh copy of the latest build.</li>
            <li>Keep <code>~/.wira</code> unless you intentionally want a clean slate.</li>
            <li>Reopen Wira and re-pair WhatsApp only if the linked session is gone.</li>
          </ol>
          <p>
            If you deliberately delete <code>~/.wira</code>, you are wiping your
            local settings, memory, pairing state, and onboarding history. That is
            the nuclear option, not the normal reinstall path.
          </p>
        </Block>

        <Block title="Who should self-serve vs who should just buy setup?">
          <ul>
            <li><b>Self-serve:</b> you are comfortable with local apps, settings files, QR pairing, and basic troubleshooting.</li>
            <li><b>Done-for-you setup:</b> you want the result, not the plumbing.</li>
          </ul>
          <p>
            Both paths are valid. This page exists so the technical buyer can see
            that there is real substance under the hood, not magic and not smoke.
          </p>
        </Block>

        <Block title="Start where you are">
          <div className="not-prose mt-4 flex flex-wrap gap-3">
            <Link to="/onboarding" className="btn-primary">
              Start setup
            </Link>
            <Link to="/learn" className="btn-ghost">
              Read the plain-language guide
            </Link>
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
      <h2 className="mb-3 text-2xl">{title}</h2>
      <div className="space-y-3 text-ink-muted [&_ol]:list-decimal [&_ol]:pl-6 [&_ol]:space-y-2 [&_ul]:list-disc [&_ul]:pl-6 [&_ul]:space-y-2">
        {children}
      </div>
    </section>
  );
}

function Code({ children }: { children: string }) {
  return (
    <pre className="overflow-x-auto rounded-3xl border border-border bg-surface px-5 py-4 text-sm leading-6 text-ink">
      <code>{children}</code>
    </pre>
  );
}
