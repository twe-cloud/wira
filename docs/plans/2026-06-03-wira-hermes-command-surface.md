# Wira → Branded Hermes Command Surface Re-architecture Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Reposition Wira from a WhatsApp reply/drafting assistant into a branded onboarding shell for a real Hermes agent that lives on the user's computer and is primarily engaged from their phone.

**Architecture:** Wira becomes the installer, pairing layer, permissioning shell, and branded runtime manager. The actual intelligence and action loop move into a dedicated local Hermes profile/process with tools, skills, memory, and guarded machine access. WhatsApp becomes the command surface, not the product itself.

**Tech Stack:** Python desktop wrapper, WhatsApp linked-device transport, Hermes Agent profiles/tools/skills/memory, local config/runtime state under `~/.wira`, project site/docs/assets for marketing and onboarding.

---

## 0. Product thesis to lock

Wira is **not** a messaging assistant, auto-reply layer, or customer support bot by default.

Wira is:
- the **first personal agent** for a solo operator
- **Hermes wrapped in Wira branding**
- installed locally on the buyer's computer
- contacted primarily from the buyer's phone over WhatsApp
- a bridge from "ChatGPT user" to "agentic operator with tools, skills, and access"
- intentionally designed so the buyer can later discover and grow into:
  - Hermes desktop
  - Hermes CLI
  - skills
  - tools
  - access control
  - automation

### Naming and identity
- In-app/local agent name: **Wira**
- Do not introduce a second starter agent name; keep Wira as product + agent until Hermes is introduced
- Hermes should remain the runtime truth and upgrade path
- Wira should act as the branded surface that reduces fear and setup friction

### Product split
Two product lanes can still exist, but both must share the same thesis:

1. **Wira Local**
   - private, owner-controlled agent on the buyer's machine
   - owner talks to agent via WhatsApp
   - agent can use permitted local tools and skills

2. **Wira Business**
   - still **not** a customer-reply bot by default
   - instead: a command surface for a solo operator/business owner
   - same Hermes-under-branding core, but with optional business context packs, automations, and governed tool access

In both lanes the primary user is the **owner/operator**, not outside contacts.

---

## 1. Current reality check

The current repo is structurally aimed at the wrong product.

### Current product center
The existing implementation is centered on:
- answering third-party WhatsApp messages on the owner's behalf
- mirroring the owner's tone through voice samples
- drafting or auto-sending replies
- approval workflows for outgoing text replies

### Evidence in current code/docs

#### Runtime
- `agent/brain.py`
  - single-prompt → single-text-reply generator
  - no Hermes conversation loop
  - no tool calling
  - no skills loading
  - no action execution layer
- `agent/prompts.py`
  - local prompt explicitly says the agent answers the owner's WhatsApp and speaks on their behalf
- `agent/whatsapp.py`
  - ignores `source.IsFromMe`
  - handles inbound contact messages as the main event stream
  - records drafts when policy blocks send
- `agent/drafts.py`, `agent/policy.py`, `agent/review.py`
  - first-class draft-review architecture

#### GUI / onboarding
- `agent/gui.py`
  - copy says Wira learns your voice and drafts replies
- `agent/onboarding.py`
  - asks for name, voice samples, reply mode
  - completion text promises draft-style usage
- `agent/setup.py`
  - asks for assistant identity + voice examples + approval mode

#### Site/docs/market positioning
- `site/docs/customer-journey.md`
- `site/docs/quickstart.md`
- `site/docs/faq.md`
- `site/docs/runbook.md`
- `agent/README.md`
- `STATUS.md`

These all reinforce the wrong mental model: reply drafting, message approval, hosted dashboard, customer-facing messaging assistant.

### Architectural verdict
The current repo is a **WhatsApp drafting/responding product** with memory and persona tuning.
It is **not yet** a branded Hermes-on-your-computer product.

---

## 2. Target architecture

## 2.1 Core system model
Wira should be re-architected as four layers:

### Layer A — Branded shell
Wira desktop app handles:
- install/update experience
- model/provider connection helper
- WhatsApp pairing helper
- local permission onboarding
- runtime status / reconnect / settings
- guided discovery of "Open in Hermes Desktop" / "Open CLI"

### Layer B — Transport bridge
WhatsApp-linked local transport handles:
- pairing session
- owner-identity lock
- command delivery to the local agent runtime
- streaming or chunked result delivery back to WhatsApp
- optional alerts / confirmations / action receipts

### Layer C — Hermes runtime
A dedicated local Hermes profile/process handles:
- conversation state
- tool calling
- skills
- memory
- cron/automation
- file/terminal/browser access as allowed
- model routing / provider auth

### Layer D — Access policy
A Wira-specific policy layer handles:
- which senders are allowed to talk to the agent
- what tools are enabled
- what folders are in scope
- whether browser/terminal are enabled
- risk levels / confirmation thresholds
- whether this is Local or Business mode

### Required mental model
User is not buying "AI texts for me."
User is buying "my first real agent, living on my machine, reachable from my phone."

---

## 2.2 Message flow

### Current flow (wrong)
Outside contact → Wira prompt → text reply or draft

### Target flow (right)
Owner WhatsApp message → Wira transport bridge → Hermes runtime → tool/skill/action execution → result back to owner WhatsApp

Examples:
- "Check today's calendar and summarize the day"
- "Search my Downloads for the latest invoice PDF"
- "Draft a follow-up email and save it"
- "Summarize open todos in this project"
- "Restart the local dev server and tell me if it comes back healthy"
- "Make me a plan for shipping this feature"

Optional future secondary mode:
- outside contacts can be supported later, but only as a deliberate extension mode, not the default product thesis

---

## 2.3 Local vs Business

### Wira Local
- single-owner, private agent surface
- paired to owner's own WhatsApp/device
- owner-issued tasks and commands only
- tool access bounded by explicit local permissions

### Wira Business
- still owner/operator-first
- optional business packs layered on top:
  - CRM helpers
  - customer memory stores
  - intake templates
  - booking/payment/reporting connectors
- same owner command surface, but with business context and workflows
- do **not** market default Wira Business as "customer auto-reply"

---

## 2.4 Organic Hermes discovery

The product should intentionally create a path from simple phone-first use to richer agent use.

### Discovery path
1. Buyer installs Wira because it feels simple
2. Buyer talks to Wira in WhatsApp
3. Buyer notices settings/pages that explain:
   - this runs on your computer
   - you can give it tools
   - you can add skills
   - you can open the same agent in desktop/CLI
4. Buyer organically graduates into Hermes-native workflows

### Product rule
Do **not** front-load jargon like MCP, agent loop, toolsets, profiles, or slash commands during onboarding.
Expose them progressively as powers the user can unlock.

---

## 3. Keep / kill / repurpose map

## 3.1 Keep largely as concepts, but repurpose
- `agent/gui.py`
  - keep as branded local shell
  - rewrite messaging copy and onboarding flow
- `agent/auth.py`
  - keep if useful for model/provider connection helper
  - may need expansion to align with Hermes-supported provider setup paths
- `agent/paths.py`
  - keep for Wira-owned local state paths
- installer/build artifacts
  - keep the local packaging direction
- release/update surface
  - keep the app-updates concept

## 3.2 Keep but redesign heavily
- `agent/whatsapp.py`
  - keep transport concept
  - rewrite around owner command bridge, not third-party reply workflow
- `agent/onboarding.py`
  - replace voice/reply-mode flow with permissions/runtime onboarding
- `agent/setup.py`
  - convert from persona/reply setup into advanced/local-admin setup or deprecate in favor of GUI
- `agent/config.py`
  - migrate from reply-policy config to runtime/access-policy config
- `agent/README.md`
  - rewrite around branded Hermes thesis
- `STATUS.md`
  - update product truth and closeout criteria
- site docs and website copy
  - rewrite to remove draft-bot positioning

## 3.3 Remove from default product center
- `agent/drafts.py`
- `agent/policy.py`
- `agent/review.py`
- draft-first messaging workflows in docs/site/runtime
- voice-sample onboarding as a default product step
- whitelist/auto-send/contact-trust as setup centerpieces

These may survive only as optional future modules for a separate responder mode.

## 3.4 New pieces needed
- Hermes runtime adapter module
- owner-lock / allowed-sender policy module
- permission model for tools/folders/browser/terminal
- Wira settings UI for access controls + runtime status
- Hermes profile/bootstrapper for Wira-managed local profile
- WhatsApp command router
- optional progressive-discovery screen(s) for CLI/Desktop/skills/tools

---

## 4. Product rewrite requirements

## 4.1 Wira Local copy rewrite
Replace this story:
- learns your voice
- drafts replies
- approves messages
- sounds like you

With this story:
- your personal agent on your computer
- reached from WhatsApp
- can work with files, apps, browser, terminal, and saved context
- starts simple, grows with you
- Wira is your first operator agent

### Suggested positioning language
- "Your first personal agent"
- "Lives on your computer. Reach it from your phone."
- "A branded path into real agentic work"
- "The easiest bridge from ChatGPT habits to a real local agent"

## 4.2 Wira Business copy rewrite
Replace:
- ops assistant / reply bot / customer-facing responder by default

With:
- owner command surface
- branded operator agent
- founder-grade private agent for running a solo business from the phone
- later optional business automations and customer workflows

### Suggested positioning language
- "Run your business from a real agent, not another dashboard"
- "Your private operator agent, reachable on WhatsApp"
- "Hermes under the hood, Wira in the hand"

---

## 5. Runtime design decisions

## 5.1 Owner lock is mandatory
Default Local and Business modes should be owner-locked.

### Rule
Only the approved owner identity should be able to issue agent commands.

### Why
Without this, the product drifts back toward:
- public messaging bot
- customer auto-replier
- trust/safety nightmare

### Verification requirement
Implementation must prove:
- owner messages are accepted
- non-owner messages are blocked or ignored
- blocked users cannot reach tools, memory, or action execution

## 5.2 Hermes runtime should be the truth
Do not keep building a parallel mini-agent inside Wira.

### Rule
Wira should bootstrap and manage a real Hermes runtime/profile rather than reinvent:
- prompting
- tool loops
- memory model
- skills
- automation
- provider abstractions

### Consequence
`brain.py` should either:
- become a thin Hermes adapter, or
- be retired entirely in favor of a Hermes session bridge

## 5.3 Permissions before tools
The user should not need agent jargon, but the product must still safely grant power.

### Onboarding should ask
- what folders can Wira access?
- allow browser access?
- allow terminal access?
- allow file edits?
- allow background jobs / automations?
- should risky actions require confirmation?

### Avoid in first-run language
- toolsets
- MCP
- profiles
- prompt engineering

### Internal mapping is fine
Wira can map simple checkboxes/toggles to Hermes toolsets and profile config.

## 5.4 Discovery surfaces must be intentional
The product must gently reveal:
- "Open the same agent in desktop"
- "Open advanced mode in CLI"
- "Add capabilities"
- "Teach your agent with skills"

This is part of the product thesis, not a side note.

---

## 6. Migration plan

## Phase 1 — Stop reinforcing the wrong product
**Goal:** Remove the draft-bot thesis from docs/copy/onboarding before more polish work deepens the wrong lane.

### Scope
- rewrite marketing copy
- rewrite onboarding copy
- update README and STATUS
- mark reply/draft mode as legacy/deferred, not core

### Files to touch
- `agent/gui.py`
- `agent/onboarding.py`
- `agent/README.md`
- `STATUS.md`
- `site/docs/customer-journey.md`
- `site/docs/quickstart.md`
- `site/docs/faq.md`
- `site/docs/runbook.md`
- relevant site landing-page source files under `site/src/`

### Deliverable
Anyone reading the repo/site should understand Wira as a branded Hermes command surface.

---

## Phase 2 — Introduce owner-command mode
**Goal:** Make the phone-to-agent interaction owner-first instead of outside-contact-first.

### Scope
- flip `whatsapp.py` logic to owner-lock mode
- handle owner-originated messages as primary workload
- route commands to a local runtime bridge
- return execution results, not drafted replies

### Key rule
The first supported happy path is:
- owner sends command to Wira
- Wira acts on the machine
- Wira reports result back

### Deliverable
Basic command surface works for private owner use.

---

## Phase 3 — Replace mini-brain with Hermes runtime adapter
**Goal:** Stop using the current reply-generator architecture as the core runtime.

### Scope
- design Wira-managed Hermes profile bootstrap
- connect provider/auth setup to Hermes configuration
- launch and manage Hermes process/session
- bridge WhatsApp commands into Hermes
- capture and relay responses back to WhatsApp

### Open design options
1. Hermes subprocess invoked per task
2. long-lived Hermes profile/session managed by Wira
3. dedicated Wira Hermes profile with guarded toolsets and workdir

### Preferred direction
Long-lived dedicated Wira Hermes profile for continuity, memory, and organic discovery.

---

## Phase 4 — Permission and settings UX
**Goal:** Make power safe and understandable.

### Scope
- Wira identity stays fixed through first-run
- owner identity lock controls
- tool access toggles
- folder access scoping
- browser/terminal/file access controls
- status screen (connected / running / last activity / reconnect)
- "Open in Hermes Desktop/CLI" discovery hooks

### Deliverable
The product feels approachable without hiding the real power.

---

## Phase 5 — Optional secondary responder mode
**Goal:** If desired later, preserve customer-reply workflows as an add-on, not the thesis.

### Rule
Responder mode is not the default Wira identity.
It is a later package/extension for specific business workflows.

### Legacy modules to revisit only here
- `drafts.py`
- `policy.py`
- `review.py`
- voice samples / tone mimicry

---

## 7. Build plan with concrete implementation slices

### Slice A — Thesis rewrite / truth alignment
**Objective:** Align repo truth with founder thesis.

**Files:**
- Modify: `STATUS.md`
- Modify: `agent/README.md`
- Modify: `site/docs/customer-journey.md`
- Modify: `site/docs/quickstart.md`
- Modify: `site/docs/faq.md`
- Modify: `site/docs/runbook.md`
- Modify: relevant `site/src/*` landing-page copy files

**Verification:**
- search the repo for `draft`, `voice`, `reply on your behalf`, `approve reply`
- categorize each hit as remove / defer / keep only for optional responder mode

### Slice B — Wira-first onboarding rewrite
**Objective:** Replace voice/reply-mode onboarding with owner-agent onboarding.

**Files:**
- Modify: `agent/gui.py`
- Modify: `agent/onboarding.py`
- Modify: `agent/setup.py`
- Modify: `agent/tests.py`

**New onboarding questions:**
- confirm Wira identity and owner lock
- choose provider/model path
- choose owner lock identity
- choose local permissions
- choose whether to expose advanced mode later

**Verification:**
- onboarding transcript no longer mentions drafting replies in your voice
- tests assert new onboarding state machine

### Slice C — Owner-lock transport
**Objective:** Make owner-issued commands the main supported runtime path.

**Files:**
- Modify: `agent/whatsapp.py`
- Modify: `agent/config.py`
- Add: owner-lock helper module
- Modify/add tests for sender validation and command routing

**Verification:**
- owner message accepted
- non-owner message blocked
- no draft record created for normal owner commands

### Slice D — Hermes bridge
**Objective:** Route WhatsApp commands into a real Hermes runtime.

**Files:**
- Add: Hermes runtime adapter module
- Add: Wira-managed Hermes profile/bootstrap module
- Modify: `agent/main.py`
- Modify: `agent/gui.py`
- Possibly retire/replace: `agent/brain.py`

**Verification:**
- can issue a simple local agent task from WhatsApp
- real tool-backed result is returned
- profile/runtime state persists locally

### Slice E — Settings and discovery
**Objective:** Let users grow from Wira into Hermes naturally.

**Files:**
- Modify: `agent/gui.py`
- Add: settings/runtime status modules if needed
- Add: settings persistence

**Verification:**
- Wira remains both the product name and the first agent name until Hermes is introduced
- can open advanced Hermes surface from Wira
- permissions/status visible in UI

---

## 8. Risks and guardrails

## P0 risks
1. **Building a parallel mini-agent instead of using Hermes**
   - fix: make Hermes runtime the source of truth
2. **Leaving third-party message reply behavior as default**
   - fix: owner-lock mode first
3. **Selling agentic power while only returning text**
   - fix: require real tool-backed actions in acceptance criteria
4. **Overexposing machine access without understandable permissions**
   - fix: simple permission UX mapped to strict internal policy

## P1 risks
1. **Marketing copy still implies reply/draft bot**
2. **Docs/site/runtime disagree with each other**
3. **Business lane drifts back into “ops assistant” vagueness**
4. **Hermes discovery is too hidden or too jargon-heavy**

---

## 9. Acceptance criteria for the new thesis

Wira should not be called complete until all are true:

1. A new buyer can understand Wira as a **personal agent on their computer**, not a WhatsApp drafting bot.
2. Wira is both the product name and the first local agent name until Hermes is introduced.
3. Local onboarding asks about permissions/runtime, not voice mimicry/reply mode.
4. Owner-issued WhatsApp messages are the main supported interaction path.
5. A real Hermes runtime/profile is doing the agent work.
6. The agent can perform at least one real local action via tools and report the result.
7. Wira intentionally exposes a growth path into Hermes Desktop/CLI.
8. Business lane copy also describes an owner command surface, not a customer auto-responder.

---

## 10. Recommended implementation order

1. Rewrite product truth/copy/docs
2. Rewrite onboarding and settings model
3. Flip WhatsApp transport to owner-lock command mode
4. Bridge to a real Hermes runtime
5. Add discovery/status/settings UX
6. Defer responder/draft workflows to optional later mode

---

## 11. Final recommendation

Do not keep polishing the current reply/draft architecture as the main line.
That would optimize the wrong product.

The winning move is:
- keep Wira as the brand and onboarding shell
- set Wira as the local identity
- make Hermes the real runtime underneath
- make WhatsApp the easiest command surface into local agentic work
- sell the product as the buyer's first real agent, not as another messaging assistant
