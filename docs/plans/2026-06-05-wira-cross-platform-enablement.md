# Wira Cross-Platform Enablement Plan

> For Hermes: use this plan to turn Wira Local from a Mac-only sales posture into a cross-platform local-agent product with explicit capability tiers by machine class.

Goal: make Wira usable on modern Apple computers and mainstream Windows machines without lying about what each machine can realistically do.

Architecture: keep one core Python runtime and one shared `~/.wira` state model, then split platform work into three lanes: macOS universal desktop packaging, Windows installer hardening, and capability-aware onboarding that routes weaker machines to cloud/ChatGPT brains instead of promising full local-model parity.

Tech stack: Python desktop app (`agent/gui.py`), PyInstaller/Inno Setup packaging, GitHub Actions release automation, shared local state in `agent/paths.py`, provider onboarding (`agent/providers.py`, `agent/auth.py`), local-model detection (`agent/local_models.py`), site copy in `site/`, and repo status/docs under `docs/` + `STATUS.md`.

---

## 1. Grounded current state

Facts verified in repo today:

- macOS packaging exists via `agent/wira.spec` and `agent/scripts/build-app.sh`.
- the public site still sells Wira as Mac-only:
  - `site/src/lib/brand.ts` says `Requires an Apple Silicon Mac (M1 or newer), macOS 12+.`
  - `site/src/components/Hero.tsx` repeats `Apple Silicon Mac only`.
  - `site/src/components/Pricing.tsx` repeats `Apple Silicon Mac only`.
  - `site/cloudflare/worker.ts` repeats the same requirement in the post-purchase download flow.
- Windows distribution already has a serious start:
  - `.github/workflows/build-windows.yml`
  - `agent/wira-win.spec`
  - `agent/wira-installer.iss`
- shared user state is already cross-platform-friendly in code because `agent/paths.py` stores config under `~/.wira` instead of app-bundle-local paths.
- local private-model setup is currently Mac-shaped:
  - `agent/local_models.py` points buyers to `https://ollama.com/download/mac`
  - copy assumes "this Mac" and recommends Apple-Silicon-friendly Ollama models.
- current automated verification is healthy: `python3 -m unittest -q` from `agent/` passed locally on 2026-06-05 with 55 tests.

Main implication:
Wira is already structurally close to cross-platform, but the product promise, local-model onboarding, and release pipeline are still biased toward Apple Silicon Macs.

---

## 2. Product rule to lock before coding

Wira should not promise identical capability on every computer.

Instead, ship explicit capability tiers:

1. Tier A — cloud brain lane
   - Works on almost any supported Mac or Windows machine.
   - Fastest path.
   - Uses Groq / OpenAI-compatible provider / ChatGPT subscription.

2. Tier B — local private lane
   - Only shown as recommended when the machine is strong enough.
   - On Apple Silicon Macs this can be a first-class path.
   - On Intel Macs and many Windows laptops this should be optional, caveated, or hidden if performance will be poor.

3. Tier C — unsupported or degraded lane
   - If packaging/runtime works but local models are unrealistic, Wira still installs and works using cloud brains.
   - If a machine cannot reliably support the GUI/runtime at all, say so plainly and do not market it as supported.

This avoids fake parity while still widening the top-of-funnel.

---

## 3. Foundation recommendation

Foundation Lane:
- Shared Python desktop shell + shared runtime core, with platform-specific packaging and capability detection.

Start From:
- existing `agent/gui.py`, `agent/paths.py`, `agent/local_models.py`, `agent/wira.spec`, `agent/wira-win.spec`, `agent/wira-installer.iss`, `.github/workflows/build-windows.yml`

Study / Harvest:
- current Mac PyInstaller path already used here
- current Windows GitHub Actions + Inno Setup path already used here
- existing provider-first onboarding copy already present in `gui.py`

Avoid:
- rewriting Wira into a new Electron/Tauri shell before proving current Python packaging is the blocker
- promising universal local-model support on Intel Macs / low-RAM Windows laptops
- marketing Windows/macOS parity before signed installers and first-run smoke checks exist

Default Verification Stack:
- `python3 -m unittest -q` in `agent/`
- local packaging smoke on macOS
- CI packaging smoke on Windows
- first-launch smoke: app opens, writes `~/.wira/.env`, saves session state, opens provider flow, reaches QR screen
- docs/site verification so product copy matches actual platform support

Internal Starter Recommendation:
- keep the current foundation; harden it instead of replacing it

Risks / Unknowns:
- Tkinter packaging and font behavior across Intel Macs / Windows display scaling
- neonize native library behavior on older Intel Macs
- whether Ollama-on-Windows should be in v1 or deferred behind provider-first support
- code signing / notarization / SmartScreen trust path still needs production hardening

---

## 4. Target support matrix

### 4.1 macOS

Support targets:
- Apple Silicon Macs: full support
- Intel Macs: support Wira app + cloud/ChatGPT brains first; local-model lane only if validated

Definition of done:
- one signed Mac artifact that launches on both Apple Silicon and Intel, or two clearly labeled Mac downloads if universal packaging is not worth the tradeoff
- onboarding copy stops saying "Apple Silicon only" unless local-private mode specifically requires it
- first-run checks explain what is available on this machine

### 4.2 Windows

Support targets:
- Windows 11 x64: primary support target
- Windows 10 x64: secondary if packaging/runtime pass cleanly

Definition of done:
- signed installer preferred; if unsigned for early beta, the site/download flow must honestly label it beta
- first launch reaches welcome screen, provider setup, and WhatsApp QR pairing
- `~/.wira` equivalent under the user's home directory works reliably

### 4.3 Capability routing

The app should decide what to recommend based on:
- OS
- CPU architecture
- RAM
- whether Ollama is installed/running
- whether ChatGPT/browser auth is available
- whether a provider API key path is the lowest-friction route

---

## 5. Implementation phases

## Phase 1 — tell the truth in-product and on-site

Objective: decouple platform support from local-model support.

Files:
- Modify: `site/src/lib/brand.ts`
- Modify: `site/src/components/Hero.tsx`
- Modify: `site/src/components/Pricing.tsx`
- Modify: `site/cloudflare/worker.ts`
- Modify: `agent/gui.py`
- Modify: `agent/README.md`
- Modify: `site/docs/quickstart.md`
- Modify: `STATUS.md`

Tasks:
1. Replace global "Apple Silicon only" claims with support language centered on the cloud/ChatGPT lane.
2. Move Apple-Silicon-only wording into the local-private-mode explanation if still true.
3. Add explicit early-support copy for Windows if installer artifacts are already part of release work.
4. Update README and status docs to define platform support separately from brain choice support.

Verification:
- search repo for stale `Apple Silicon Mac only` / `this Mac` claims in buyer-facing copy
- build site and confirm updated wording appears in generated output

## Phase 2 — add machine capability detection

Objective: make onboarding honest and automatic.

Files:
- Modify: `agent/gui.py`
- Modify: `agent/local_models.py`
- Create: `agent/platform_support.py`
- Test: `agent/tests.py`

Tasks:
1. Create a small platform-support module that reports:
   - OS
   - architecture
   - RAM
   - local-model recommendation level
   - copy snippets for supported / limited / unsupported lanes
2. Update `gui.py` so the welcome and brain-choice screens say:
   - what works on this computer now
   - what is optional
   - what is not recommended
3. Split local-model messaging from Mac-only assumptions in `local_models.py`.
4. Add tests for Intel Mac, Apple Silicon Mac, Windows x64, and low-RAM scenarios.

Verification:
- unit tests cover support-matrix decisions
- manual smoke shows different copy for mocked machine classes

## Phase 3 — finish the Mac broadening lane

Objective: support more Apple hardware without breaking the good Apple-Silicon path.

Files:
- Modify: `agent/wira.spec`
- Modify: `agent/scripts/build-app.sh`
- Modify: release docs/scripts as needed
- Test: `agent/tests.py` if packaging metadata is asserted there

Tasks:
1. Decide universal2 vs dual-download Mac distribution.
2. Validate whether `neonize` and Tk packaging run cleanly on Intel Macs.
3. If universal2 is messy, ship separate clearly named Mac downloads:
   - `Wira-mac-apple-silicon`
   - `Wira-mac-intel`
4. Keep local-private onboarding as Apple-Silicon-preferred until Intel validation proves otherwise.

Verification:
- artifact launches on tested Mac classes
- first-run flow completes without manual env hacks

## Phase 4 — harden Windows as a first-class lane

Objective: move Windows from "workflow exists" to "buyer-safe beta or GA".

Files:
- Modify: `.github/workflows/build-windows.yml`
- Modify: `agent/wira-win.spec`
- Modify: `agent/wira-installer.iss`
- Modify: `agent/README.md`
- Modify: release notes/docs
- Test: `agent/tests.py` if platform path logic changes

Tasks:
1. Verify the generated installer actually launches `gui.py` and persists state outside the install dir.
2. Confirm WhatsApp DLL download/versioning is pinned and reproducible.
3. Add a Windows smoke checklist to release docs.
4. Decide whether Ollama-on-Windows is in scope now or deferred.
5. If deferred, make provider-first / ChatGPT-first onboarding the default Windows story.

Verification:
- CI artifact builds cleanly
- real Windows smoke proves launch, provider selection, QR pairing, and restart persistence

## Phase 5 — release plumbing and download routing

Objective: make public download links platform-aware.

Files:
- Modify: `site/src/lib/brand.ts`
- Modify: `site/cloudflare/worker.ts`
- Modify: any release scripts that publish artifacts

Tasks:
1. Expand download routing from a single Mac route to platform-aware routes.
2. Keep stable product-owned URLs, for example:
   - `/download/wira-mac`
   - `/download/wira-windows`
   - optional `/download/wira-mac-intel`
3. Add platform labels on the success page and official product page.
4. Ensure public routes can change release origins without changing the sales page.

Verification:
- each download route resolves to the correct current artifact
- success flow shows the right options without confusion

---

## 6. Acceptance criteria

Wira can be called cross-platform when all of the following are true:

- buyer-facing copy no longer falsely says the whole product is Apple-Silicon-only
- Mac support is explicit by machine class
- Windows support is explicit by machine class
- onboarding detects machine capability and recommends the right brain path
- at least one tested Windows install path works end to end
- at least one tested Intel Mac path works end to end, or Intel is explicitly excluded with a grounded reason
- download routes and docs match the real artifact matrix

---

## 7. Recommended shipping order

1. Phase 1 — fix the truth surface
2. Phase 2 — machine capability detection
3. Phase 4 — Windows hardening
4. Phase 3 — Intel/universal Mac decision
5. Phase 5 — download routing cleanup

Reason:
- the biggest blocker is currently messaging accuracy, not core architecture
- Windows is already partially scaffolded in repo
- Mac broadening depends on testing whether Intel is truly worth supporting beyond cloud-brain mode

---

## 8. Immediate next move

If starting implementation now, begin with Phase 1 plus the support-matrix helper from Phase 2.

That yields the fastest honest win:
- the site stops underselling the product as Mac-only
- the app stops overpromising local-private parity
- future Windows/Intel work slots into a clean support model instead of ad hoc copy edits
