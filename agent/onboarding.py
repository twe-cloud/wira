"""Wira onboarding — first conversation happens IN WhatsApp.

After the QR scan, Wira messages the owner to collect:
1. Their name
2. A few example messages (voice training)
3. Which contacts to auto-reply to

This replaces the terminal-based setup.py for GUI installs.
The onboarding state is tracked in the memory DB.
"""

import json
import logging
import os
import sqlite3
import time
from pathlib import Path

from paths import update_env

logger = logging.getLogger("wira.onboarding")

ONBOARDING_DB = Path.home() / ".wira" / "onboarding.json"

STEPS = [
    {
        "key": "name",
        "message": (
            "Hey! I'm Wira, your new WhatsApp AI assistant. "
            "I'll be handling messages on this number for you.\n\n"
            "First — what's your name? (This is how I'll refer to you when talking to your contacts.)"
        ),
    },
    {
        "key": "voice",
        "message": (
            "Nice to meet you, {name}! Now I need to learn how you type.\n\n"
            "Send me 3-5 of your recent WhatsApp replies — just paste them one after another. "
            "I'll match your tone, length, and style.\n\n"
            "When you're done, send: *done*"
        ),
    },
    {
        "key": "mode",
        "message": (
            "Got it — I've learned your style.\n\n"
            "One last thing: how should I handle replies?\n\n"
            "*1* — Draft everything (I write it, you review before it sends)\n"
            "*2* — Auto-reply to trusted contacts, draft for new people\n"
            "*3* — Auto-reply to everyone (fastest)\n\n"
            "Send 1, 2, or 3."
        ),
    },
]

DONE_MESSAGE = (
    "All set, {name}! I'm live on your WhatsApp now.\n\n"
    "Here's what happens next:\n"
    "• When someone messages you, I'll draft a reply in your voice\n"
    "• You'll see drafts in this chat — just forward them or I'll learn to send directly\n"
    "• To change settings, just tell me (e.g. \"auto-reply to +1234567890\")\n\n"
    "I'm here whenever you need me."
)


def _load_state() -> dict:
    if ONBOARDING_DB.exists():
        try:
            return json.loads(ONBOARDING_DB.read_text())
        except Exception:
            pass
    return {}


def _save_state(state: dict):
    ONBOARDING_DB.parent.mkdir(parents=True, exist_ok=True)
    ONBOARDING_DB.write_text(json.dumps(state, indent=2))


def is_onboarding_complete() -> bool:
    state = _load_state()
    return state.get("complete", False)


def get_current_step() -> int:
    state = _load_state()
    return state.get("step", 0)


def get_step_message(step: int, state: dict) -> str:
    if step >= len(STEPS):
        return DONE_MESSAGE.format(name=state.get("name", "there"))
    msg = STEPS[step]["message"]
    return msg.format(**{k: state.get(k, "") for k in ["name"]})


def process_onboarding_reply(text: str) -> str | None:
    """Process an onboarding reply from the owner. Returns the next message to send,
    or None if onboarding is complete."""
    state = _load_state()
    step = state.get("step", 0)

    if step >= len(STEPS):
        return None  # Already done

    step_info = STEPS[step]
    key = step_info["key"]

    if key == "name":
        state["name"] = text.strip()
        update_env("OWNER_NAME", state["name"])
        state["step"] = step + 1
        _save_state(state)
        return get_step_message(step + 1, state)

    elif key == "voice":
        if text.strip().lower() == "done":
            # Save collected voice samples
            samples = state.get("voice_samples", [])
            voice_text = "\n".join(samples)
            update_env("VOICE_SAMPLES", voice_text)
            state["step"] = step + 1
            _save_state(state)
            return get_step_message(step + 1, state)
        else:
            # Collect voice sample
            samples = state.get("voice_samples", [])
            samples.append(text.strip())
            state["voice_samples"] = samples
            _save_state(state)
            count = len(samples)
            if count < 3:
                return f"Got it ({count} so far). Send more, or send *done* when finished."
            return None  # Don't reply to every sample after 3

    elif key == "mode":
        modes = {"1": "draft", "2": "auto-trusted", "3": "auto-all"}
        mode = modes.get(text.strip(), "draft")
        state["mode"] = mode
        update_env("APPROVAL_MODE", mode)
        state["step"] = step + 1
        state["complete"] = True
        _save_state(state)
        return DONE_MESSAGE.format(name=state.get("name", "there"))

    return None


def _update_env(key: str, value: str):
    """Update a key in the .env file."""
    update_env(key, value)


def send_welcome():
    """Send the first onboarding message to the owner.
    Called after QR scan completes."""
    if is_onboarding_complete():
        return

    state = _load_state()
    if state.get("step", 0) > 0:
        return  # Already in progress

    state["step"] = 0
    state["started"] = time.time()
    _save_state(state)

    # The welcome message will be sent by the WhatsApp handler
    # when it detects the owner's first interaction
    logger.info("Onboarding initialized — waiting for owner's first message")
