#!/usr/bin/env python3
"""Wira setup — connect the local runtime and go.

1. Connect a brain
2. Confirm owner + agent identity
3. Pick a local access level
4. Scan the WhatsApp QR code

That's it. Wira is the easiest path into a real local agent reached from your phone.
"""

import os
import sys
from pathlib import Path

from paths import ENV_FILE, write_env

DEFAULT_AGENT_NAME = "Wira"


def banner():
    print()
    print("  ╔══════════════════════════════════════╗")
    print("  ║          W I R A   S E T U P         ║")
    print("  ║   Your first local agent            ║")
    print("  ╚══════════════════════════════════════╝")
    print()


def step_brain():
    print("  STEP 1 — Connect your brain")
    print("  ─────────────────────────────")
    print()
    print("  Wira needs a brain for the local Hermes runtime.")
    print("  The easiest option is your ChatGPT subscription (no API key needed).")
    print()
    print("  [1] ChatGPT subscription (recommended)")
    print("  [2] Anthropic Claude API key")
    print("  [3] OpenAI API key")
    print("  [4] Local Ollama (private, runs on your machine)")
    print()

    choice = input("  Choose [1-4, default 1]: ").strip() or "1"

    if choice == "1":
        provider = "chatgpt"
        print()
        print("  Signing in to ChatGPT...")
        from auth import device_code_login, is_logged_in
        if is_logged_in():
            reuse = input("  Already signed in. Use existing session? [Y/n]: ").strip().lower()
            if reuse != "n":
                print("  Using existing ChatGPT session.")
                return provider, {}
        device_code_login()
        print()
        print("  ChatGPT connected!")
        return provider, {}

    if choice == "2":
        key = input("  Anthropic API key: ").strip()
        if not key:
            print("  No key entered. Aborting.")
            sys.exit(1)
        return "anthropic", {"ANTHROPIC_API_KEY": key}

    if choice == "3":
        key = input("  OpenAI API key: ").strip()
        if not key:
            print("  No key entered. Aborting.")
            sys.exit(1)
        return "openai", {"OPENAI_API_KEY": key}

    if choice == "4":
        host = input("  Ollama host [http://localhost:11434]: ").strip() or "http://localhost:11434"
        return "ollama", {"OLLAMA_HOST": host}

    print("  Invalid choice.")
    sys.exit(1)


def step_identity():
    print()
    print("  STEP 2 — Owner and agent identity")
    print("  ───────────────────────────────────")
    print()

    owner = input("  Your name: ").strip() or "there"
    assistant = input(f"  Agent name [{DEFAULT_AGENT_NAME}]: ").strip() or DEFAULT_AGENT_NAME
    return owner, assistant


def step_permissions():
    print()
    print("  STEP 3 — Local access level")
    print("  ────────────────────────────")
    print()
    print("  [1] Desk mode     — lightweight help only")
    print("  [2] Balanced mode — file reading + web help")
    print("  [3] Operator mode — files + web + terminal")
    print()
    preset_choice = input("  Choose [1-3, default 2]: ").strip() or "2"
    preset = {"1": "desk", "2": "balanced", "3": "operator"}.get(preset_choice, "balanced")
    print()
    print("  Risky actions:")
    print("  [1] Confirm first (recommended)")
    print("  [2] Move fast unless something is unclear")
    confirm_choice = input("  Choose [1-2, default 1]: ").strip() or "1"
    require_confirmation = confirm_choice != "2"
    return preset, require_confirmation


def write_config(provider, extra_env, owner, assistant, preset, require_confirmation):
    lines = [
        f"OWNER_NAME={owner}",
        f"ASSISTANT_NAME={assistant}",
        f"LLM_PROVIDER={provider}",
        "WIRA_PROMPT_PROFILE=local",
        "WIRA_OWNER_LOCK_ENABLED=true",
        "WIRA_EXTERNAL_MODE=ignore",
        f"WIRA_PERMISSION_PRESET={preset}",
        f"WIRA_REQUIRE_CONFIRMATION={'true' if require_confirmation else 'false'}",
        "DISCLOSE_AI=true",
    ]
    for k, v in extra_env.items():
        lines.append(f"{k}={v}")
    write_env(lines)
    print()
    print(f"  Config saved to {ENV_FILE}")


def step_whatsapp():
    print()
    print("  STEP 4 — Connect WhatsApp")
    print("  ───────────────────────────")
    print()
    print("  When you press Enter, Wira will start and show a QR code.")
    print("  Scan it with WhatsApp > Linked Devices > Link a Device.")
    print()
    input("  Press Enter to start Wira...")


def main():
    banner()
    provider, extra_env = step_brain()
    owner, assistant = step_identity()
    preset, require_confirmation = step_permissions()
    write_config(provider, extra_env, owner, assistant, preset, require_confirmation)
    step_whatsapp()
    print()
    print("  Starting Wira...")
    print("  ────────────────")
    print()
    os.execvp(sys.executable, [sys.executable, str(Path(__file__).parent / "main.py")])


if __name__ == "__main__":
    main()
