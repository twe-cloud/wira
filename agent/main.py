#!/usr/bin/env python3
"""Wira — your AI assistant on WhatsApp.

Loads config, wires up the brain + memory + WhatsApp transport, and runs.
"""

import logging

from paths import load_env

# Load user-owned config before importing config.
load_env()

import config
from drafts import Drafts
from runtime_bridge import HermesRuntime
from whatsapp import WhatsApp

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("wira")


def main():
    logger.info("=" * 50)
    logger.info("  %s — local Hermes agent on WhatsApp", config.ASSISTANT_NAME)
    logger.info("  Owner: %s | Brain: %s (%s)", config.OWNER_NAME, config.LLM_PROVIDER, config.LLM_MODEL)
    logger.info(
        "  Owner lock: %s | Permission preset: %s | Confirmation: %s",
        config.WIRA_OWNER_LOCK_ENABLED,
        config.WIRA_PERMISSION_PRESET,
        config.WIRA_REQUIRE_CONFIRMATION,
    )
    logger.info("=" * 50)

    drafts = Drafts()
    runtime = HermesRuntime()
    wa = WhatsApp(runtime, drafts)

    try:
        wa.run()
    except KeyboardInterrupt:
        logger.info("Shutting down. Bye.")


if __name__ == "__main__":
    main()
