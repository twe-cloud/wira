#!/usr/bin/env python3
"""Wira — your AI assistant on WhatsApp.

Loads config, wires up the brain + memory + WhatsApp transport, and runs.
"""

import logging

from paths import load_env

# Load user-owned config before importing config.
load_env()

import config
from brain import Brain
from drafts import Drafts
from memory import Memory
from whatsapp import WhatsApp

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("wira")


def main():
    logger.info("=" * 50)
    logger.info("  %s — AI assistant for WhatsApp", config.ASSISTANT_NAME)
    logger.info("  Owner: %s | Brain: %s (%s)", config.OWNER_NAME, config.LLM_PROVIDER, config.LLM_MODEL)
    logger.info("  Approval: %s | Trusted contacts: %d",
                config.APPROVAL_MODE, len(config.AUTO_SEND_TO))
    logger.info("=" * 50)

    memory = Memory()
    drafts = Drafts()
    brain = Brain(memory)
    wa = WhatsApp(brain, drafts)

    try:
        wa.run()
    except KeyboardInterrupt:
        logger.info("Shutting down. Bye.")


if __name__ == "__main__":
    main()
