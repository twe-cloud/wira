# Wira Customer Journey

Updated: 2026-06-01

## Product Split

Wira has two activation paths:

- **Wira Local:** owner-controlled install. The buyer downloads Wira, connects
  a brain, scans a WhatsApp Linked Devices QR code, and finishes setup in
  WhatsApp.
- **Wira Business:** managed hosted setup. Stripe payment starts provisioning,
  then Ni Biashara confirms the business map, WhatsApp number/provider path,
  approval policy, and launch checks before widening automation.

## Local Buyer Experience

1. Buy Wira Local.
2. Land on `/products/wira/start/?tier=self`.
3. Download installer.
4. Connect ChatGPT, an API key, or a local model.
5. Scan WhatsApp QR.
6. Wira asks for owner name, voice samples, and reply mode.

Fastest safe default: `APPROVAL_MODE=draft` until the owner trusts the replies.

## Hosted Buyer Experience

1. Buy Wira Business or scope first.
2. Land on `/products/wira/start/?tier=managed`.
3. Stripe webhook confirms paid checkout and starts provisioning.
4. Ni Biashara collects:
   - business display name
   - current WhatsApp number and account ownership
   - first workflow
   - business facts and policies
   - stop points and owner escalation rules
   - optional tool add-ons
5. Launch starts draft-first.
6. Auto-send widens only after real message smoke tests pass.

## Customer-Visible Identity

End customers see the client business's WhatsApp display name. They should not
see Wira or Hermes unless the business explicitly chooses a customer-facing
assistant name.

Recommended mapping:

| Surface | Name shown |
| --- | --- |
| Customer WhatsApp chat | Client business name |
| Owner/admin product | Wira |
| Internal engine/runtime | Hidden |

## Tool Connection Order

1. WhatsApp channel.
2. Business facts and reply policy.
3. Payment/deposit link or website/order form.
4. CRM, booking, SMS, or voice.

Do not force optional tools into first activation unless the first workflow
depends on them.

## Smoke Checks Before Wider Automation

- Webhook challenge passes.
- Signed inbound message verification passes where configured.
- Business prompt uses `BUSINESS_NAME`.
- Draft creation works for the first workflow.
- Owner approves one outbound send.
- Sensitive data exclusions are visible and honored.
