"""WhatsApp transport for Wira, via neonize (whatsmeow).

First run prints a QR code in the terminal — scan it from
WhatsApp > Linked Devices and Wira is live on that number.
"""

import logging

from neonize.client import NewClient
from neonize.events import ConnectedEv, MessageEv

import config
from drafts import Drafts
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

    def _on_message(self, client: NewClient, event: MessageEv):
        try:
            self._handle(client, event)
        except Exception as e:
            logger.exception("Failed to handle message: %s", e)

    def _handle(self, client: NewClient, event: MessageEv):
        info = event.Info
        source = info.MessageSource

        if source.IsFromMe:  # our own outgoing messages — never reply to ourselves
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
