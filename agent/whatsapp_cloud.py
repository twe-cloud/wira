"""Official WhatsApp Business Cloud API transport for Wira.

This transport is for managed business numbers. The existing whatsapp.py
module remains the personal QR-linked path.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import sqlite3
from dataclasses import dataclass
from contextlib import closing
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs

import httpx

import config
from drafts import Drafts
from policy import should_auto_send

logger = logging.getLogger("wira.whatsapp_cloud")


class WebhookError(ValueError):
    """Raised for rejected webhook requests."""


@dataclass(frozen=True)
class CloudMessage:
    message_id: str
    from_number: str
    sender_name: str
    text: str
    phone_number_id: str
    raw: dict[str, Any]


class CloudMessageStore:
    """Tiny idempotency store for inbound WhatsApp message IDs."""

    def __init__(self, path: str | None = None):
        self.path = path or config.WHATSAPP_CLOUD_DB_PATH
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with closing(sqlite3.connect(self.path)) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS inbound_messages (
                    message_id TEXT PRIMARY KEY,
                    from_number TEXT NOT NULL,
                    received_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.commit()

    def mark_seen(self, message_id: str, from_number: str) -> bool:
        """Return True the first time a message ID is seen."""
        try:
            with closing(sqlite3.connect(self.path)) as conn:
                conn.execute(
                    "INSERT INTO inbound_messages (message_id, from_number) VALUES (?, ?)",
                    (message_id, from_number),
                )
                conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False


class CloudApiTransport:
    """Minimal sender for Meta's Graph WhatsApp messages endpoint."""

    def __init__(
        self,
        access_token: str | None = None,
        phone_number_id: str | None = None,
        graph_version: str | None = None,
        client: httpx.Client | None = None,
    ):
        self.access_token = access_token or config.WHATSAPP_CLOUD_ACCESS_TOKEN
        self.phone_number_id = phone_number_id or config.WHATSAPP_CLOUD_PHONE_NUMBER_ID
        self.graph_version = graph_version or config.WHATSAPP_CLOUD_GRAPH_VERSION
        self.client = client or httpx.Client(timeout=20.0)
        if not self.access_token:
            raise RuntimeError("WHATSAPP_CLOUD_ACCESS_TOKEN is required")
        if not self.phone_number_id:
            raise RuntimeError("WHATSAPP_CLOUD_PHONE_NUMBER_ID is required")

    @property
    def messages_url(self) -> str:
        return f"https://graph.facebook.com/{self.graph_version}/{self.phone_number_id}/messages"

    def send_text(self, to_number: str, body: str) -> dict[str, Any]:
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": normalize_number(to_number),
            "type": "text",
            "text": {"preview_url": False, "body": body},
        }
        response = self.client.post(
            self.messages_url,
            headers={
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
            },
            json=payload,
        )
        response.raise_for_status()
        return response.json()


def normalize_number(value: str) -> str:
    return "".join(ch for ch in value if ch.isdigit())


def verify_webhook_challenge(query_string: str, expected_token: str) -> str:
    query = parse_qs(query_string, keep_blank_values=True)
    mode = (query.get("hub.mode") or [""])[0]
    token = (query.get("hub.verify_token") or [""])[0]
    challenge = (query.get("hub.challenge") or [""])[0]

    if mode != "subscribe" or not challenge:
        raise WebhookError("invalid webhook verification request")
    if not expected_token or not hmac.compare_digest(token, expected_token):
        raise WebhookError("invalid webhook verify token")
    return challenge


def verify_meta_signature(
    raw_body: bytes,
    signature_header: str,
    app_secret: str,
    require_signature: bool = False,
) -> None:
    """Verify X-Hub-Signature-256 when an app secret is configured."""
    if not app_secret:
        if require_signature:
            raise WebhookError("WHATSAPP_CLOUD_APP_SECRET is required to verify Meta webhook signatures")
        return
    if not signature_header.startswith("sha256="):
        raise WebhookError("missing Meta webhook signature")
    expected = "sha256=" + hmac.new(app_secret.encode(), raw_body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(signature_header, expected):
        raise WebhookError("invalid Meta webhook signature")


def parse_cloud_messages(payload: dict[str, Any]) -> list[CloudMessage]:
    messages: list[CloudMessage] = []
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            metadata = value.get("metadata", {})
            phone_number_id = str(metadata.get("phone_number_id", ""))
            contacts = {
                str(contact.get("wa_id", "")): contact.get("profile", {}).get("name", "")
                for contact in value.get("contacts", [])
            }
            for raw_message in value.get("messages", []):
                text = _message_text(raw_message)
                if not text:
                    continue
                from_number = normalize_number(str(raw_message.get("from", "")))
                message_id = str(raw_message.get("id", ""))
                if not from_number or not message_id:
                    continue
                messages.append(
                    CloudMessage(
                        message_id=message_id,
                        from_number=from_number,
                        sender_name=contacts.get(from_number) or from_number,
                        text=text,
                        phone_number_id=phone_number_id,
                        raw=raw_message,
                    )
                )
    return messages


def _message_text(raw_message: dict[str, Any]) -> str:
    msg_type = raw_message.get("type")
    if msg_type == "text":
        return str(raw_message.get("text", {}).get("body", "")).strip()
    if msg_type == "button":
        return str(raw_message.get("button", {}).get("text", "")).strip()
    if msg_type == "interactive":
        interactive = raw_message.get("interactive", {})
        button = interactive.get("button_reply", {})
        row = interactive.get("list_reply", {})
        return str(button.get("title") or row.get("title") or "").strip()
    return ""


def handle_cloud_payload(
    payload: dict[str, Any],
    brain,
    transport: CloudApiTransport,
    store: CloudMessageStore | None = None,
    drafts: Drafts | None = None,
) -> dict[str, int]:
    store = store or CloudMessageStore()
    drafts = drafts or Drafts()
    stats = {"received": 0, "ignored_duplicates": 0, "sent": 0, "drafted": 0}

    for message in parse_cloud_messages(payload):
        stats["received"] += 1
        if not store.mark_seen(message.message_id, message.from_number):
            stats["ignored_duplicates"] += 1
            continue

        reply = brain.reply(message.from_number, message.sender_name, message.text)
        if should_auto_send(message.from_number):
            transport.send_text(message.from_number, reply)
            stats["sent"] += 1
        else:
            drafts.record(
                message.from_number,
                message.from_number,
                message.sender_name,
                message.text,
                reply,
            )
            stats["drafted"] += 1

    return stats


def parse_json_body(raw_body: bytes) -> dict[str, Any]:
    try:
        body = json.loads(raw_body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise WebhookError("invalid JSON body") from exc
    if not isinstance(body, dict):
        raise WebhookError("webhook body must be a JSON object")
    return body
