"""Small webhook server for WhatsApp Business Cloud API.

Run locally for smoke tests or behind a managed HTTPS surface:

    python cloud_webhook.py
"""

from __future__ import annotations

import json
import logging
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

import config
from brain import Brain
from memory import Memory
from whatsapp_cloud import (
    CloudApiTransport,
    CloudMessageStore,
    WebhookError,
    handle_cloud_payload,
    parse_json_body,
    verify_meta_signature,
    verify_webhook_challenge,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("wira.cloud_webhook")


class WiraCloudWebhookHandler(BaseHTTPRequestHandler):
    brain = None
    transport = None
    store = None

    def log_message(self, fmt, *args):
        logger.info("%s - %s", self.address_string(), fmt % args)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path != config.WHATSAPP_CLOUD_WEBHOOK_PATH:
            self._json(404, {"error": "not found"})
            return
        try:
            challenge = verify_webhook_challenge(
                parsed.query,
                config.WHATSAPP_CLOUD_VERIFY_TOKEN,
            )
        except WebhookError as exc:
            self._json(403, {"error": str(exc)})
            return
        body = challenge.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != config.WHATSAPP_CLOUD_WEBHOOK_PATH:
            self._json(404, {"error": "not found"})
            return

        raw_body = self.rfile.read(int(self.headers.get("Content-Length", "0")))
        try:
            verify_meta_signature(
                raw_body,
                self.headers.get("X-Hub-Signature-256", ""),
                config.WHATSAPP_CLOUD_APP_SECRET,
                config.WHATSAPP_CLOUD_REQUIRE_SIGNATURE,
            )
            payload = parse_json_body(raw_body)
            stats = handle_cloud_payload(
                payload,
                self.brain,
                self.transport,
                self.store,
            )
        except WebhookError as exc:
            logger.warning("Rejected WhatsApp webhook: %s", exc)
            self._json(400, {"error": str(exc)})
            return
        except Exception:
            logger.exception("Failed to process WhatsApp webhook")
            self._json(500, {"error": "webhook processing failed"})
            return

        self._json(200, {"status": "ok", **stats})

    def _json(self, status: int, payload: dict):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def build_server() -> ThreadingHTTPServer:
    if not config.WHATSAPP_CLOUD_VERIFY_TOKEN:
        raise RuntimeError("WHATSAPP_CLOUD_VERIFY_TOKEN is required")
    if config.WHATSAPP_CLOUD_REQUIRE_SIGNATURE and not config.WHATSAPP_CLOUD_APP_SECRET:
        raise RuntimeError("WHATSAPP_CLOUD_APP_SECRET is required when signature verification is enabled")
    WiraCloudWebhookHandler.brain = Brain(Memory())
    WiraCloudWebhookHandler.transport = CloudApiTransport()
    WiraCloudWebhookHandler.store = CloudMessageStore()
    return ThreadingHTTPServer(
        (config.WHATSAPP_CLOUD_HOST, config.WHATSAPP_CLOUD_PORT),
        WiraCloudWebhookHandler,
    )


def main():
    server = build_server()
    host, port = server.server_address
    logger.info("Wira WhatsApp Cloud webhook listening on %s:%s%s", host, port, config.WHATSAPP_CLOUD_WEBHOOK_PATH)
    server.serve_forever()


if __name__ == "__main__":
    main()
