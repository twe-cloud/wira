#!/usr/bin/env python3
"""Wira setup — connect three dots and go.

1. Sign in with your ChatGPT account (or choose another brain)
2. Enter your business name and a few example replies
3. Scan the WhatsApp QR code

That's it. Wira is live on your WhatsApp number.
"""

import os
import sys
from pathlib import Path

from paths import ENV_FILE, WIRA_DIR, write_env


def banner():
    print()
    print("  ╔══════════════════════════════════════╗")
    print("  ║          W I R A   S E T U P         ║")
    print("  ║   WhatsApp AI for your business      ║")
    print("  ╚══════════════════════════════════════╝")
    print()


def step_brain():
    """Step 1: Connect the brain."""
    print("  STEP 1 — Connect your brain")
    print("  ─────────────────────────────")
    print()
    print("  Wira needs a brain to generate replies.")
    print("  The easiest option is your ChatGPT subscription (no API key needed).")
    print()
    print("  [1] ChatGPT subscription (recommended — you already pay for it)")
    print("  [2] Anthropic Claude API key")
    print("  [3] OpenAI API key")
    print("  [4] Local Ollama (free, private, runs on your machine)")
    print()

    choice = input("  Choose [1-4, default 1]: ").strip() or "1"

    if choice == "1":
        provider = "chatgpt"
        print()
        print("  Signing in to ChatGPT...")
        # Import here so httpx is only needed for ChatGPT flow
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

    elif choice == "2":
        provider = "anthropic"
        key = input("  Anthropic API key: ").strip()
        if not key:
            print("  No key entered. Aborting.")
            sys.exit(1)
        return provider, {"ANTHROPIC_API_KEY": key}

    elif choice == "3":
        provider = "openai"
        key = input("  OpenAI API key: ").strip()
        if not key:
            print("  No key entered. Aborting.")
            sys.exit(1)
        return provider, {"OPENAI_API_KEY": key}

    elif choice == "4":
        provider = "ollama"
        host = input("  Ollama host [http://localhost:11434]: ").strip() or "http://localhost:11434"
        return provider, {"OLLAMA_HOST": host}

    else:
        print("  Invalid choice.")
        sys.exit(1)


def step_identity():
    """Step 2: Business identity and voice."""
    print()
    print("  STEP 2 — Your business identity")
    print("  ──────────────────────────────────")
    print()

    owner = input("  Your name (customers see this): ").strip()
    if not owner:
        owner = "there"

    assistant = input("  Assistant name [Wira]: ").strip() or "Wira"

    print()
    print("  Voice training — paste 3-5 of your recent WhatsApp replies.")
    print("  This teaches Wira your tone. One per line, empty line to finish:")
    print()

    samples = []
    while True:
        line = input("  > ").strip()
        if not line:
            break
        samples.append(line)

    return owner, assistant, "\n".join(samples)


def step_behavior():
    """Step 2b: Approval mode."""
    print()
    print("  How should Wira handle replies?")
    print()
    print("  [1] Draft all — you review every reply before it sends (safest)")
    print("  [2] Auto-trusted — instant replies to contacts you trust, drafts for new people")
    print("  [3] Auto-all — send everything (fast but risky)")
    print()

    choice = input("  Choose [1-3, default 1]: ").strip() or "1"
    modes = {"1": "draft", "2": "auto-trusted", "3": "auto-all"}
    return modes.get(choice, "draft")


def write_env(provider, extra_env, owner, assistant, voice, approval_mode):
    """Write the .env file."""
    lines = [
        f"OWNER_NAME={owner}",
        f"ASSISTANT_NAME={assistant}",
        f"LLM_PROVIDER={provider}",
        f"APPROVAL_MODE={approval_mode}",
        f"DISCLOSE_AI=true",
    ]

    if voice:
        lines.append(f"VOICE_SAMPLES={voice}")

    for k, v in extra_env.items():
        lines.append(f"{k}={v}")

    write_env(lines)
    print()
    print(f"  Config saved to {ENV_FILE}")


def step_whatsapp():
    """Step 3: WhatsApp pairing."""
    print()
    print("  STEP 3 — Connect WhatsApp")
    print("  ───────────────────────────")
    print()
    print("  When you press Enter, Wira will start and show a QR code.")
    print("  Scan it with WhatsApp > Linked Devices > Link a Device.")
    print()
    print("  After that, Wira is live on your WhatsApp number.")
    print()
    input("  Press Enter to start Wira...")


def main():
    banner()

    # Step 1: Brain
    provider, extra_env = step_brain()

    # Step 2: Identity
    owner, assistant, voice = step_identity()

    # Step 2b: Behavior
    approval_mode = step_behavior()

    # Write config
    write_env(provider, extra_env, owner, assistant, voice, approval_mode)

    # Step 3: WhatsApp
    step_whatsapp()

    # Launch
    print()
    print("  Starting Wira...")
    print("  ────────────────")
    print()
    os.execvp(sys.executable, [sys.executable, str(Path(__file__).parent / "main.py")])


if __name__ == "__main__":
    main()
