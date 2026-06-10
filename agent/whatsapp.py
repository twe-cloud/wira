"""WhatsApp transport for Wira, via neonize (whatsmeow).

Default local mode is owner-locked: the linked owner talks to their own local
Hermes-backed agent from WhatsApp. Legacy external draft/reply behavior is kept
behind WIRA_EXTERNAL_MODE for later optional responder workflows.
"""

import logging

from neonize.client import NewClient
from neonize.events import ConnectedEv, MessageEv

import config
from brain import Brain
from drafts import Drafts
from memory import Memory
from onboarding import is_onboarding_complete, process_onboarding_reply, get_step_message, _load_state
from policy import should_auto_send

logger = logging.getLogger("wira.whatsapp")


class WhatsApp:
    def __init__(self, brain, drafts: Drafts | None = None):
        self.brain = brain
        self.drafts = drafts or Drafts()
        # Lazily-built plain responder for non-owner messages (see
        # _external_responder). Kept separate from the owner's operator runtime.
        self._responder = None
        self.client = NewClient(config.SESSION_DB_PATH)
        self.client.event(ConnectedEv)(self._on_connected)
        self.client.event(MessageEv)(self._on_message)

    def _external_responder(self):
        """Responder for non-owner messages.

        Non-owner/customer text must never reach the owner's operator runtime
        (which can run terminal/file commands), so if the owner runtime is the
        Hermes operator we build a separate plain LLM responder for these
        replies. When the runtime is already a plain responder, we reuse it.
        """
        if self._responder is not None:
            return self._responder
        if getattr(self.brain, "is_operator_runtime", False):
            self._responder = Brain(Memory())
        else:
            self._responder = self.brain
        return self._responder

    def _on_connected(self, client: NewClient, _event: ConnectedEv):
        logger.info("Connected to WhatsApp as %s. %s is live.", config.OWNER_NAME, config.ASSISTANT_NAME)

        if not is_onboarding_complete():
            import threading
            def _send_welcome():
                import time
                time.sleep(3)
                try:
                    state = _load_state()
                    if state.get("step", 0) == 0:
                        msg = get_step_message(0, state)
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

    @staticmethod
    def _extract_text(event: MessageEv) -> str:
        text = event.Message.conversation or event.Message.extendedTextMessage.text
        return (text or "").strip()

    @staticmethod
    def _chat_key(source) -> str:
        chat = source.Chat
        return getattr(chat, "User", "") or str(chat)

    def _is_owner_message(self, source) -> bool:
        if not config.WIRA_OWNER_LOCK_ENABLED:
            return True
        return bool(getattr(source, "IsFromMe", False))

    def _handle_owner_message(self, client: NewClient, event: MessageEv, text: str):
        info = event.Info
        source = info.MessageSource
        sender_name = info.Pushname or config.OWNER_NAME or "Owner"
        chat_key = self._chat_key(source)

        if not is_onboarding_complete():
            logger.info("Onboarding message from %s: %s", sender_name, text)
            response = process_onboarding_reply(text)
            if response:
                client.reply_message(response, event)
            return

        logger.info("Owner command from %s: %s", sender_name, text)
        reply = self.brain.reply(chat_key, sender_name, text)
        client.reply_message(reply, event)

    def _handle_external_message(self, client: NewClient, event: MessageEv, text: str):
        info = event.Info
        source = info.MessageSource
        chat = source.Chat
        sender_number = getattr(source.Sender, "User", "") or getattr(chat, "User", "")
        sender_name = info.Pushname or sender_number or "there"
        chat_key = self._chat_key(source)

        if not is_onboarding_complete():
            logger.info("Ignoring external message during onboarding from %s", sender_name)
            return

        mode = config.WIRA_EXTERNAL_MODE
        if mode == "ignore":
            logger.info("Blocked non-owner message from %s (owner-lock local mode)", sender_name)
            return

        if config.ALLOWLIST and sender_number not in config.ALLOWLIST:
            logger.info("Ignoring message from %s (not in allowlist)", sender_number)
            return

        # Never route non-owner text through the operator runtime.
        reply = self._external_responder().reply(chat_key, sender_name, text)
        if mode == "auto" or should_auto_send(sender_number):
            client.reply_message(reply, event)
            return

        self.drafts.record(chat_key, sender_number, sender_name, text, reply)
        logger.info("Drafted reply for %s (external mode=%s)", sender_name, mode)

    def _handle(self, client: NewClient, event: MessageEv):
        info = event.Info
        source = info.MessageSource

        if source.IsGroup and not config.REPLY_TO_GROUPS:
            return

        text = self._extract_text(event)
        if not text:
            return

        if self._is_owner_message(source):
            self._handle_owner_message(client, event, text)
            return

        self._handle_external_message(client, event, text)

    def run(self):
        """Connect and block forever, processing messages."""
        logger.info("Starting WhatsApp connection (scan the QR code if prompted)...")
        self.client.connect()
        try:
            from neonize.events import event as _keepalive

            _keepalive.wait()
        except Exception:
            pass
