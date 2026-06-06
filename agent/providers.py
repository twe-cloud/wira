"""OpenAI-compatible provider helpers for Wira onboarding.

The brain (brain.py) already drives every OpenAI-compatible provider through one
client path — they differ only by base_url + key. This module adds the buyer-
facing layer: which presets to surface, where to get a key, how to save the
choice, and a no-side-effect connection test before Wira commits.

Kept separate from brain.py so the test path never touches conversation memory.
"""

from __future__ import annotations

import logging
import os

import config

logger = logging.getLogger("wira.providers")

# Where a buyer gets an API key for each provider (shown as a clickable link).
KEY_URLS = {
    "openrouter": "https://openrouter.ai/keys",
    "groq": "https://console.groq.com/keys",
    "deepseek": "https://platform.deepseek.com/api_keys",
    "xai": "https://console.x.ai",
    "together": "https://api.together.ai/settings/api-keys",
    "fireworks": "https://fireworks.ai/account/api-keys",
    "mistral": "https://console.mistral.ai/api-keys",
    "gemini": "https://aistudio.google.com/app/apikey",
    "lmstudio": "https://lmstudio.ai",
    "openai-compatible": "",
}

# One-line "why this one" for the onboarding cards.
TAGLINES = {
    "openrouter": "One key, hundreds of models (Claude, Gemini, GPT) with fallback.",
    "groq": "Extremely fast, generous free tier.",
    "deepseek": "Very cheap and strong.",
    "xai": "Grok models from xAI.",
    "together": "Hosted open models.",
    "fireworks": "Fast hosted open models.",
    "mistral": "Mistral's hosted models.",
    "gemini": "Google Gemini via its OpenAI-compatible endpoint.",
    "lmstudio": "Local models served by LM Studio on this computer — private and free.",
    "openai-compatible": "Point Wira at any OpenAI-compatible endpoint.",
}

# Ordered presets to show in the brain-choice screen (best value first).
ONBOARDING_PRESETS = ["openrouter", "groq", "deepseek"]


_LOOPBACK_HOSTS = {"localhost", "127.0.0.1", "::1", "[::1]"}


def base_url_ok(url: str) -> tuple[bool, str]:
    """Reject plaintext http:// to a non-loopback host (would leak the API key).

    Loopback (LM Studio / local servers) over http is fine; everything remote
    must be https. Returns (ok, message).
    """
    from urllib.parse import urlparse

    try:
        parsed = urlparse(url)
    except Exception:
        return False, "That base URL could not be parsed."
    if parsed.scheme == "https":
        return True, ""
    if parsed.scheme == "http":
        host = (parsed.hostname or "").lower()
        if host in _LOOPBACK_HOSTS:
            return True, ""
        return False, (
            "For your security, remote endpoints must use https:// — plaintext "
            "http:// would send your API key in the clear. Use https, or a local "
            "(localhost) server."
        )
    return False, "Base URL must start with https:// (or http:// for a local server)."


def preset(provider: str) -> dict:
    """Merge config registry + UI metadata for one provider."""
    cfg = config.OPENAI_COMPATIBLE_PROVIDERS.get(provider, {})
    return {
        "id": provider,
        "label": cfg.get("label", provider),
        "key_env": cfg.get("key_env"),
        "default_model": cfg.get("default_model", ""),
        "needs_key": cfg.get("key_env") is not None,
        "needs_base_url": cfg.get("base_url") is None,
        "key_url": KEY_URLS.get(provider, ""),
        "tagline": TAGLINES.get(provider, ""),
    }


def all_presets() -> list[dict]:
    return [preset(p) for p in config.OPENAI_COMPATIBLE_PROVIDERS]


def save_provider(
    provider: str,
    api_key: str | None = None,
    model: str | None = None,
    base_url: str | None = None,
) -> None:
    """Commit Wira to an OpenAI-compatible provider, writing the needed env keys."""
    from paths import update_env

    cfg = config.OPENAI_COMPATIBLE_PROVIDERS[provider]

    # Defence in depth: never persist a custom endpoint that would leak the key
    # over plaintext http to a remote host (the UI tests first, but guard here too).
    if cfg["base_url"] is None and base_url:
        ok, why = base_url_ok(base_url.strip())
        if not ok:
            raise ValueError(why)

    update_env("LLM_PROVIDER", provider)
    update_env("LLM_MODEL", model or cfg["default_model"])

    if cfg["key_env"] and api_key:
        update_env(cfg["key_env"], api_key.strip())
    if cfg["base_url"] is None and base_url:
        update_env("OPENAI_BASE_URL", base_url.strip())
    logger.info("Wira brain set to %s (%s)", provider, cfg["label"])


def lmstudio_running() -> bool:
    """True if an LM Studio (or other) server answers at localhost:1234."""
    try:
        import httpx

        resp = httpx.get("http://localhost:1234/v1/models", timeout=2.0)
        return resp.status_code == 200
    except Exception:
        return False


def test_provider(
    provider: str,
    api_key: str | None = None,
    base_url: str | None = None,
    model: str | None = None,
) -> tuple[bool, str]:
    """Confirm a provider answers a trivial prompt. No memory side effects.

    Returns (ok, message). Never raises.
    """
    cfg = config.OPENAI_COMPATIBLE_PROVIDERS.get(provider)
    if not cfg:
        return False, f"Unknown provider {provider!r}."

    resolved_base = cfg["base_url"] or base_url or config.OPENAI_BASE_URL
    if not resolved_base:
        return False, "No base URL set for this provider."

    # Built-in presets are trusted (all https / loopback). For a user-supplied
    # custom base URL, refuse plaintext http to a remote host — it would leak the key.
    if cfg["base_url"] is None:
        ok, why = base_url_ok(resolved_base)
        if not ok:
            return False, why

    if cfg["key_env"]:
        key = (api_key or os.getenv(cfg["key_env"], "")).strip()
        if not key:
            return False, "An API key is required."
    else:
        key = "not-needed"

    test_model = model or cfg["default_model"]
    try:
        from openai import OpenAI

        client = OpenAI(api_key=key, base_url=resolved_base)
        resp = client.chat.completions.create(
            model=test_model,
            max_tokens=16,
            messages=[{"role": "user", "content": "Say hi in one word."}],
        )
        content = resp.choices[0].message.content or ""
        if content.strip():
            return True, f"Connected to {cfg['label']}."
        return False, "The provider responded but returned no text."
    except Exception as e:
        msg = str(e)
        if "401" in msg or "Unauthorized" in msg or "invalid_api_key" in msg:
            return False, "That key was rejected. Check the key and try again."
        if "model" in msg.lower() and ("not" in msg.lower() or "exist" in msg.lower()):
            return False, f"Model {test_model!r} isn't available on this account."
        logger.warning("Provider test failed (%s): %s", provider, msg)
        return False, f"Could not reach {cfg['label']}: {msg[:160]}"
