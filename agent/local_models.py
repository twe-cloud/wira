"""Local-model recommendation + setup for Wira — the private, free brain path.

Wira's brain (brain.py) already speaks Ollama. Ollama is the natural local model
runtime on a Mac, so this module doesn't ship its own loader the way Hapo Ndani's
desktop app bundles llama.cpp — it detects an Ollama install, recommends a small
catalog of chat-capable models, pulls one with progress, and smoke-tests it before
Wira commits to the local brain.

The whole point: let a buyer run Wira entirely on their own machine — no ChatGPT
subscription relay, no per-message cost, nothing leaving the Mac — when they want
that. Detection is best-effort and never raises; callers branch on the returned
status.
"""

from __future__ import annotations

import json
import logging
import shutil
from dataclasses import dataclass

import config

logger = logging.getLogger("wira.local_models")

OLLAMA_DOWNLOAD_URL = "https://ollama.com/download/mac"


@dataclass(frozen=True)
class LocalModel:
    """A recommended Ollama model, tiered by the RAM it comfortably wants."""

    tag: str          # Ollama pull tag, e.g. "llama3.2:3b"
    name: str         # Human label
    size_label: str   # Approximate on-disk size for the UI
    min_ram_gb: int   # Recommended minimum unified memory
    note: str         # One-line "why this one"


# Small, instruction-following models that answer WhatsApp messages well and fit
# on a typical Apple-Silicon Mac. Ordered easiest-first; the GUI recommends the
# first entry that fits the detected RAM.
RECOMMENDED_MODELS: list[LocalModel] = [
    LocalModel(
        tag="llama3.2:3b",
        name="Llama 3.2 3B",
        size_label="~2 GB",
        min_ram_gb=8,
        note="Fast and light — a good default on any M1 or newer Mac.",
    ),
    LocalModel(
        tag="qwen2.5:7b",
        name="Qwen 2.5 7B",
        size_label="~4.7 GB",
        min_ram_gb=16,
        note="Stronger reasoning for richer replies; wants 16 GB+.",
    ),
    LocalModel(
        tag="llama3.1:8b",
        name="Llama 3.1 8B",
        size_label="~4.7 GB",
        min_ram_gb=16,
        note="Well-rounded general assistant; wants 16 GB+.",
    ),
]


def ollama_installed() -> bool:
    """True if the Ollama CLI is on PATH (a strong signal it's installed)."""
    return shutil.which("ollama") is not None


def ollama_running() -> bool:
    """True if the Ollama daemon answers at OLLAMA_HOST."""
    try:
        import httpx

        resp = httpx.get(f"{config.OLLAMA_HOST}/api/tags", timeout=2.0)
        return resp.status_code == 200
    except Exception:
        return False


def installed_models() -> list[str]:
    """Tags of models already pulled into the local Ollama (empty if unreachable)."""
    try:
        import httpx

        resp = httpx.get(f"{config.OLLAMA_HOST}/api/tags", timeout=3.0)
        if resp.status_code != 200:
            return []
        data = resp.json()
        return [m.get("name", "") for m in data.get("models", []) if m.get("name")]
    except Exception:
        return []


def system_ram_gb() -> int:
    """Best-effort unified-memory size in GB (0 if it can't be determined)."""
    try:
        import os

        total_bytes = os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")
        return int(total_bytes / (1024 ** 3))
    except Exception:
        return 0


def recommended_for_ram(ram_gb: int | None = None) -> LocalModel:
    """Pick the strongest recommended model that fits the machine's RAM."""
    ram = ram_gb if ram_gb is not None else system_ram_gb()
    fits = [m for m in RECOMMENDED_MODELS if ram == 0 or m.min_ram_gb <= ram]
    # Prefer a mid-size model on roomy machines, else the lightest that fits.
    if ram >= 16:
        for m in RECOMMENDED_MODELS:
            if m.tag == "qwen2.5:7b":
                return m
    return fits[0] if fits else RECOMMENDED_MODELS[0]


@dataclass
class Detection:
    installed: bool
    running: bool
    models: list[str]
    ram_gb: int
    recommended: LocalModel

    @property
    def available(self) -> bool:
        """Local brain is usable right now (daemon up)."""
        return self.running

    @property
    def has_recommended(self) -> bool:
        return self.recommended.tag in self.models


def detect() -> Detection:
    """Snapshot the local-model situation on this Mac. Never raises."""
    installed = ollama_installed()
    running = ollama_running()
    models = installed_models() if running else []
    ram = system_ram_gb()
    return Detection(
        installed=installed,
        running=running,
        models=models,
        ram_gb=ram,
        recommended=recommended_for_ram(ram),
    )


def pull_model(tag: str, progress_cb=None) -> bool:
    """Pull a model into Ollama, streaming progress to ``progress_cb``.

    ``progress_cb`` is called with (status: str, completed: int, total: int).
    Returns True on success. Never raises — returns False on any failure.
    """
    try:
        import httpx

        with httpx.stream(
            "POST",
            f"{config.OLLAMA_HOST}/api/pull",
            json={"model": tag, "stream": True},
            timeout=None,
        ) as resp:
            if resp.status_code != 200:
                logger.warning("Ollama pull failed: HTTP %s", resp.status_code)
                return False
            for line in resp.iter_lines():
                if not line:
                    continue
                try:
                    evt = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if evt.get("error"):
                    logger.warning("Ollama pull error: %s", evt["error"])
                    return False
                if progress_cb:
                    progress_cb(
                        evt.get("status", ""),
                        int(evt.get("completed", 0) or 0),
                        int(evt.get("total", 0) or 0),
                    )
                if evt.get("status") == "success":
                    return True
        # Stream ended without an explicit "success" — verify by listing.
        return tag in installed_models()
    except Exception as e:
        logger.warning("Ollama pull exception: %s", e)
        return False


def smoke_test(tag: str) -> bool:
    """Confirm the model actually answers a trivial prompt. Never raises."""
    try:
        import httpx

        resp = httpx.post(
            f"{config.OLLAMA_HOST}/api/chat",
            json={
                "model": tag,
                "messages": [{"role": "user", "content": "Say hi in one word."}],
                "stream": False,
            },
            timeout=60.0,
        )
        if resp.status_code != 200:
            return False
        content = (resp.json().get("message", {}) or {}).get("content", "")
        return bool(content.strip())
    except Exception as e:
        logger.warning("Ollama smoke test failed: %s", e)
        return False


def select_local_brain(tag: str) -> None:
    """Commit Wira to the local Ollama brain on the given model tag."""
    from paths import update_env

    update_env("LLM_PROVIDER", "ollama")
    update_env("LLM_MODEL", tag)
    logger.info("Wira brain set to local Ollama model %s", tag)
