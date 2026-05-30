"""Send-or-draft policy. Extracted so it's testable without neonize."""

import config


def should_auto_send(sender_number: str) -> bool:
    """Return True if Wira should fire the reply on WhatsApp now,
    or False if it should be queued as a draft for human approval."""
    mode = config.APPROVAL_MODE
    if mode == "auto-all":
        return True
    if mode == "draft":
        return False
    # "auto-trusted" (default): only auto-send to known trusted numbers
    return sender_number in config.AUTO_SEND_TO
