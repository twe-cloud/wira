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
    def __init__(self, memory: Memory, prompt_profile: str | None = None):
        self.memory = memory
        self.provider = config.LLM_PROVIDER
        self.prompt_profile = prompt_profile or config.WIRA_PROMPT_PROFILE
        self._client = self._build_client()
        logger.info(
            "Brain ready (provider=%s, model=%s, prompt_profile=%s)",
            self.provider,
            config.LLM_MODEL,
            self.prompt_profile,
        )

    def _build_client(self):
        if self.provider == "chatgpt":
            from auth import get_access_token, cloudflare_headers, CODEX_BASE_URL
            from openai import OpenAI

            token = get_access_token()
            if not token:
                raise RuntimeError(
                    "ChatGPT login required. Run: python setup.py"
                )
            return OpenAI(
                api_key=token,
                base_url=CODEX_BASE_URL,
                default_headers=cloudflare_headers(token),
            )
        elif self.provider == "anthropic":
            if not config.ANTHROPIC_API_KEY:
                raise RuntimeError(
                    "LLM_PROVIDER=anthropic but ANTHROPIC_API_KEY is not set. "
                    "Add it to .env, or switch LLM_PROVIDER=chatgpt or LLM_PROVIDER=ollama."
                )
            from anthropic import Anthropic

            return Anthropic(api_key=config.ANTHROPIC_API_KEY)
        elif self.provider == "openai":
            if not config.OPENAI_API_KEY:
                raise RuntimeError(
                    "LLM_PROVIDER=openai but OPENAI_API_KEY is not set. "
                    "Add it to .env, or switch LLM_PROVIDER=chatgpt or LLM_PROVIDER=ollama."
                )
            from openai import OpenAI

            return OpenAI(api_key=config.OPENAI_API_KEY)
        elif self.provider == "ollama":
            from ollama import Client

            return Client(host=config.OLLAMA_HOST)
        raise RuntimeError(
            f"Unknown LLM_PROVIDER: {self.provider!r} (use 'chatgpt', 'anthropic', 'openai', or 'ollama')"
        )

    def reply(self, chat: str, sender_name: str, text: str) -> str:
        """Generate Wira' reply to one message and persist the exchange."""
        history = self.memory.get_recent(chat)
        self.memory.save(chat, "user", text)

        sys = system_prompt(self.prompt_profile) + (
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

    def _rebuild_chatgpt_client(self):
        """Refresh ChatGPT token and rebuild the client."""
        from auth import get_access_token, cloudflare_headers, CODEX_BASE_URL
        from openai import OpenAI

        token = get_access_token()
        if not token:
            raise RuntimeError("ChatGPT token refresh failed. Run: python setup.py")
        self._client = OpenAI(
            api_key=token,
            base_url=CODEX_BASE_URL,
            default_headers=cloudflare_headers(token),
        )

    def _generate(self, sys: str, history: list[dict], text: str) -> str:
        if self.provider == "chatgpt":
            return self._generate_chatgpt(sys, history, text)
        elif self.provider == "anthropic":
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

    def _generate_chatgpt(self, sys: str, history: list[dict], text: str) -> str:
        """Generate via ChatGPT subscription with automatic token refresh."""
        messages = [{"role": "system", "content": sys}]
        messages += history
        messages.append({"role": "user", "content": text})

        try:
            resp = self._client.chat.completions.create(
                model=config.LLM_MODEL,
                max_tokens=config.MAX_TOKENS,
                messages=messages,
            )
            return resp.choices[0].message.content or ""
        except Exception as e:
            # Token might have expired — refresh and retry once
            if "401" in str(e) or "403" in str(e) or "Unauthorized" in str(e):
                logger.info("ChatGPT token expired, refreshing...")
                self._rebuild_chatgpt_client()
                resp = self._client.chat.completions.create(
                    model=config.LLM_MODEL,
                    max_tokens=config.MAX_TOKENS,
                    messages=messages,
                )
                return resp.choices[0].message.content or ""
            raise
