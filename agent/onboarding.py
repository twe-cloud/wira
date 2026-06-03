"""Wira onboarding — first private setup conversation happens in WhatsApp.

After the QR scan, Wira messages the owner to finish first-run setup for a
local Hermes-backed agent that lives on their computer.
"""

import json
import logging
import time
from pathlib import Path

from paths import update_env

logger = logging.getLogger("wira.onboarding")

ONBOARDING_DB = Path.home() / ".wira" / "onboarding.json"
DEFAULT_AGENT_NAME = "Wira"

PERMISSION_PRESETS = {
    "1": ("desk", "Desk mode"),
    "2": ("balanced", "Balanced mode"),
    "3": ("operator", "Operator mode"),
}

STEPS = [
    {
        "key": "name",
        "message": (
            f"Hey! I'm {DEFAULT_AGENT_NAME}, your new local agent on this computer.\n\n"
            "First: what's your name?"
        ),
    },
    {
        "key": "permissions",
        "message": (
            f"Nice to meet you, {{name}}. Your WhatsApp agent is *{DEFAULT_AGENT_NAME}*.\n\n"
            "Choose the access level for Wira on this computer.\n\n"
            "*1* — Desk mode: lightweight help and memory, no direct machine actions\n"
            "*2* — Balanced mode: can read files and use the web when helpful\n"
            "*3* — Operator mode: can use files, web, and terminal on this machine\n\n"
            "Send 1, 2, or 3."
        ),
    },
    {
        "key": "confirmation",
        "message": (
            "How cautious should I be with risky actions?\n\n"
            "*1* — Confirm risky actions first (recommended)\n"
            "*2* — Move fast and only pause when something is unclear\n\n"
            "Send 1 or 2."
        ),
    },
]

DONE_MESSAGE = (
    "All set, {name}! {assistant_name} is live on your WhatsApp now.\n\n"
    "What this means:\n"
    "• {assistant_name} is a real local agent running on your computer\n"
    "• Your phone is the easiest way to reach it\n"
    "• You can start with commands like: \"check Downloads for the latest invoice\" or \"summarize my day\"\n\n"
    "When you're ready for the deeper runtime, Wira can introduce Hermes."
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
        return DONE_MESSAGE.format(
            name=state.get("name", "there"),
            assistant_name=state.get("assistant_name", DEFAULT_AGENT_NAME),
        )
    msg = STEPS[step]["message"]
    return msg.format(
        name=state.get("name", "there"),
        assistant_name=state.get("assistant_name", DEFAULT_AGENT_NAME),
    )


def process_onboarding_reply(text: str) -> str | None:
    """Process an onboarding reply from the owner.

    Returns the next message to send, or None if onboarding is already complete.
    """
    state = _load_state()
    step = state.get("step", 0)

    if step >= len(STEPS):
        return None

    key = STEPS[step]["key"]
    value = text.strip()

    if key == "name":
        state["name"] = value or "there"
        state["assistant_name"] = DEFAULT_AGENT_NAME
        update_env("OWNER_NAME", state["name"])
        update_env("ASSISTANT_NAME", DEFAULT_AGENT_NAME)
        update_env("WIRA_PROMPT_PROFILE", "local")
        update_env("WIRA_EXTERNAL_MODE", "ignore")
        update_env("WIRA_OWNER_LOCK_ENABLED", "true")
        state["step"] = step + 1
        _save_state(state)
        return get_step_message(step + 1, state)

    if key == "permissions":
        preset, label = PERMISSION_PRESETS.get(value, PERMISSION_PRESETS["2"])
        state["permission_preset"] = preset
        state["permission_label"] = label
        update_env("WIRA_PERMISSION_PRESET", preset)
        state["step"] = step + 1
        _save_state(state)
        return get_step_message(step + 1, state)

    if key == "confirmation":
        require_confirmation = value != "2"
        state["require_confirmation"] = require_confirmation
        update_env("WIRA_REQUIRE_CONFIRMATION", "true" if require_confirmation else "false")
        state["step"] = step + 1
        state["complete"] = True
        _save_state(state)
        return DONE_MESSAGE.format(
            name=state.get("name", "there"),
            assistant_name=state.get("assistant_name", DEFAULT_AGENT_NAME),
        )

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
    if state.get("step", 0) > 0 or state.get("started"):
        return

    state["step"] = 0
    state["started"] = time.time()
    _save_state(state)

    logger.info("Onboarding initialized — waiting for owner's first message")
