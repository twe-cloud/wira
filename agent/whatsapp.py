"""WhatsApp transport for Wira, via neonize (whatsmeow).

First run prints a QR code in the terminal — scan it from
WhatsApp > Linked Devices and Wira is live on that number.
"""

import logging

from neonize.client import NewClient
from neonize.events import ConnectedEv, MessageEv

import config
from drafts import Drafts
from onboarding import is_onboarding_complete, process_onboarding_reply, get_step_message, _load_state
from policy import should_auto_send

logger = logging.getLogger("wira.whatsapp")


class WhatsApp:
    def __init__(self, brain, drafts: Drafts | None = None):
        self.brain = brain
        self.drafts = drafts or Drafts()
        self.client = NewClient(config.SESSION_DB_PATH)
        self.client.event(ConnectedEv)(self._on_connected)
        self.client.event(MessageEv)(self._on_message)

    def _on_connected(self, client: NewClient, _event: ConnectedEv):
        logger.info("Connected to WhatsApp as %s. Wira is live.", config.OWNER_NAME)

        # Send onboarding welcome if this is a first-time setup
        if not is_onboarding_complete():
            import threading
            def _send_welcome():
                import time
                time.sleep(3)  # Wait for connection to stabilize
                try:
                    state = _load_state()
                    if state.get("step", 0) == 0:
                        msg = get_step_message(0, state)
                        # Send to the owner's own number (the linked device)
                        jid = client.get_me()
                        if jid:
                            client.send_message(jid, msg)
                            logger.info("Sent onboarding welcome message")
                except Exception as e:
                    logger.warning("Could not send onboarding welcome: %s", e)
            threading.Thread(target=_send_welcome, daemon=True).start()

    def _on_message(self, client: NewClient, event: MessageEv):
        try:
            self._handle(client, event)
        except Exception as e:
            logger.exception("Failed to handle message: %s", e)

    def _handle(self, client: NewClient, event: MessageEv):
        info = event.Info
        source = info.MessageSource

        # Our own outgoing messages — check if this is the first connection
        # and send the onboarding welcome
        if source.IsFromMe:
            return
        if source.IsGroup and not config.REPLY_TO_GROUPS:
            return

        text = event.Message.conversation or event.Message.extendedTextMessage.text
        if not text.strip():
            return  # non-text (image/sticker/etc.) — ignore for now

        chat = source.Chat
        sender_number = getattr(source.Sender, "User", "") or getattr(chat, "User", "")
        if config.ALLOWLIST and sender_number not in config.ALLOWLIST:
            logger.info("Ignoring message from %s (not in allowlist)", sender_number)
            return

        sender_name = info.Pushname or sender_number or "there"
        chat_key = getattr(chat, "User", "") or str(chat)

        # --- Onboarding: if not complete, handle as onboarding conversation ---
        if not is_onboarding_complete():
            logger.info("Onboarding message from %s: %s", sender_name, text)
            response = process_onboarding_reply(text)
            if response:
                client.reply_message(response, event)
            return

        logger.info("Message from %s: %s", sender_name, text)
        reply = self.brain.reply(chat_key, sender_name, text)

        if should_auto_send(sender_number):
            logger.info("Replying to %s: %s", sender_name, reply)
            client.reply_message(reply, event)
        else:
            self.drafts.record(chat_key, sender_number, sender_name, text, reply)
            logger.info(
                "Drafted reply for %s (approval mode = %s) — not sent",
                sender_name, config.APPROVAL_MODE,
            )

    def run(self):
        """Connect and block forever, processing messages."""
        logger.info("Starting WhatsApp connection (scan the QR code if prompted)...")
        self.client.connect()
        # In most builds connect() blocks until disconnect. If it returns early,
        # park on neonize's keep-alive event so the process stays up.
        try:
            from neonize.events import event as _keepalive

            _keepalive.wait()
        except Exception:
            pass
