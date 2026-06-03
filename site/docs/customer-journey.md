# Wira Customer Journey

Updated: 2026-06-03

## Product thesis

Wira is not a WhatsApp auto-reply bot.

Wira is a branded path into real agentic work:
- a local agent that lives on the buyer's computer
- reached from the buyer's phone over WhatsApp
- powered by a real Hermes runtime under Wira branding
- designed so the buyer can grow naturally into Hermes Desktop, CLI, tools, skills, and local access over time

## Product Split

Wira has two activation paths:

- **Wira Local:** owner-controlled install. The buyer downloads Wira, connects a brain, pairs WhatsApp, grants local permissions, and starts talking to their agent from their phone.
- **Wira Business:** still owner/operator-first. Same branded Hermes command surface, but with business-specific context packs, workflows, and governed access for a solo operator.

In both lanes, the primary user is the **owner/operator**, not outside contacts.

## Local Buyer Experience

1. Buy Wira Local.
2. Land on `/products/wira/start/?tier=self`.
3. Download installer.
4. Connect ChatGPT, an API key, or a local model.
5. Scan WhatsApp QR.
6. Confirm owner lock, default agent identity (Vera), and safe local permissions.
7. Start issuing real tasks from WhatsApp.

The first delight moment should be:
- owner sends a task from the phone
- Vera uses the local runtime on the computer
- Vera reports back with a real result

## Business Buyer Experience

1. Buy Wira Business or scope first.
2. Land on `/products/wira/start/?tier=managed`.
3. Complete the same local/owner-first setup path.
4. Add business context and optional workflow packs.
5. Start using Wira as the private operating surface for the founder or solo operator.

Business mode is still not a default customer auto-reply product. Customer-facing workflows, if any, are later extensions—not the core thesis.

## Customer-Visible Identity

Recommended mapping:

| Surface | Name shown |
| --- | --- |
| Owner WhatsApp chat | Vera (renameable after setup) |
| Desktop app / installer | Wira |
| Underlying runtime | Hermes (discoverable later, not forced first) |

The product should feel simple on day one while making the deeper Hermes path discoverable over time.

## Tool Connection Order

1. WhatsApp channel.
2. Brain/provider connection.
3. Owner lock.
4. Local permissions and safe defaults.
5. Optional folders, browser, terminal, and skills.
6. Optional business workflow packs.

Do not force advanced agent jargon in the first activation flow.

## Smoke Checks Before Expansion

- WhatsApp pairing succeeds.
- Owner-issued messages reach the local runtime.
- One real task runs successfully on the connected machine.
- Result comes back to WhatsApp clearly.
- Safe defaults are visible: owner lock, permission boundaries, and reconnect path.
- Buyer can discover that the same agent can later be opened in Desktop/CLI.
