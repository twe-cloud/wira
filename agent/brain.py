"""Wira' brain — turns an incoming WhatsApp message into a reply.

Pluggable LLM backend: Anthropic (Claude) for quality, or Ollama for a
fully local/private setup. Memory is per-contact, so each conversation
keeps its own thread of context.
"""

import logging
from datetime import datetime

import config
from memory import Memory
from prompts import system_prompt

logger = logging.getLogger("wira.brain")


class Brain:
    def __init__(self, memory: Memory):
        self.memory = memory
        self.provider = config.LLM_PROVIDER
        self._client = self._build_client()
        logger.info("Brain ready (provider=%s, model=%s)", self.provider, config.LLM_MODEL)

    def _build_client(self):
        if self.provider == "anthropic":
            if not config.ANTHROPIC_API_KEY:
                raise RuntimeError(
                    "LLM_PROVIDER=anthropic but ANTHROPIC_API_KEY is not set. "
                    "Add it to .env, or switch LLM_PROVIDER=openai or LLM_PROVIDER=ollama."
                )
            from anthropic import Anthropic

            return Anthropic(api_key=config.ANTHROPIC_API_KEY)
        elif self.provider == "openai":
            if not config.OPENAI_API_KEY:
                raise RuntimeError(
                    "LLM_PROVIDER=openai but OPENAI_API_KEY is not set. "
                    "Add it to .env, or switch LLM_PROVIDER=anthropic or LLM_PROVIDER=ollama."
                )
            from openai import OpenAI

            return OpenAI(api_key=config.OPENAI_API_KEY)
        elif self.provider == "ollama":
            from ollama import Client

            return Client(host=config.OLLAMA_HOST)
        raise RuntimeError(
            f"Unknown LLM_PROVIDER: {self.provider!r} (use 'anthropic', 'openai', or 'ollama')"
        )

    def reply(self, chat: str, sender_name: str, text: str) -> str:
        """Generate Wira' reply to one message and persist the exchange."""
        history = self.memory.get_recent(chat)
        self.memory.save(chat, "user", text)

        sys = system_prompt() + (
            f"\n\nContext: right now it is {datetime.now():%A, %B %d %Y, %I:%M %p}. "
            f"You are chatting with {sender_name}."
        )

        try:
            reply = self._generate(sys, history, text)
        except Exception as e:  # network / provider hiccup — fail soft, don't crash the bridge
            logger.error("LLM error: %s", e)
            return f"(one sec — {config.OWNER_NAME} will get back to you shortly)"

        reply = (reply or "").strip() or f"({config.OWNER_NAME} will get back to you on this.)"
        self.memory.save(chat, "assistant", reply)
        return reply

    def _generate(self, sys: str, history: list[dict], text: str) -> str:
        if self.provider == "anthropic":
            messages = history + [{"role": "user", "content": text}]
            resp = self._client.messages.create(
                model=config.LLM_MODEL,
                max_tokens=config.MAX_TOKENS,
                system=sys,
                messages=messages,
            )
            return "".join(block.text for block in resp.content if block.type == "text")
        elif self.provider == "openai":
            messages = [{"role": "system", "content": sys}]
            messages += history
            messages.append({"role": "user", "content": text})
            resp = self._client.chat.completions.create(
                model=config.LLM_MODEL,
                max_tokens=config.MAX_TOKENS,
                messages=messages,
            )
            return resp.choices[0].message.content or ""
        else:  # ollama
            messages = [{"role": "system", "content": sys}]
            messages += history
            messages.append({"role": "user", "content": text})
            resp = self._client.chat(model=config.LLM_MODEL, messages=messages)
            return resp.message.content
