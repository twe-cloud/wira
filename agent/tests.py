"""Tests for Wira core (memory, persona, brain provider selection).

Stdlib-only — no pytest required. Run with: python -m unittest tests.py
"""

import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

# Isolate test state from any real config / live DBs
os.environ["MEMORY_DB_PATH"] = tempfile.mktemp(suffix="_wira_test.db")
os.environ["OWNER_NAME"] = "TestOwner"
os.environ["ASSISTANT_NAME"] = "TestWira"
os.environ["ANTHROPIC_API_KEY"] = ""  # unset for guard tests
os.environ["LLM_PROVIDER"] = "anthropic"

sys.path.insert(0, os.path.dirname(__file__))

# Re-import config fresh after env tweaks
import importlib

import config  # noqa: E402

importlib.reload(config)
import brain  # noqa: E402
import drafts as drafts_mod  # noqa: E402
import memory  # noqa: E402
import policy  # noqa: E402
import prompts  # noqa: E402
import whatsapp_cloud  # noqa: E402

importlib.reload(memory)
importlib.reload(prompts)
importlib.reload(brain)
importlib.reload(drafts_mod)
importlib.reload(policy)
importlib.reload(whatsapp_cloud)


class MemoryTests(unittest.TestCase):
    def setUp(self):
        self.db = tempfile.mktemp(suffix=".db")
        self.mem = memory.Memory(self.db)

    def test_save_and_recall_chronological(self):
        self.mem.save("alice", "user", "hello")
        self.mem.save("alice", "assistant", "hi back")
        self.mem.save("alice", "user", "how are you")
        got = self.mem.get_recent("alice")
        self.assertEqual(
            got,
            [
                {"role": "user", "content": "hello"},
                {"role": "assistant", "content": "hi back"},
                {"role": "user", "content": "how are you"},
            ],
        )

    def test_per_chat_isolation(self):
        self.mem.save("alice", "user", "alice msg")
        self.mem.save("bob", "user", "bob msg")
        self.assertEqual(self.mem.get_recent("alice"), [{"role": "user", "content": "alice msg"}])
        self.assertEqual(self.mem.get_recent("bob"), [{"role": "user", "content": "bob msg"}])

    def test_recent_window_limit(self):
        for i in range(50):
            self.mem.save("chat", "user", f"msg {i}")
        got = self.mem.get_recent("chat", n=5)
        self.assertEqual(len(got), 5)
        self.assertEqual(got[-1]["content"], "msg 49")
        self.assertEqual(got[0]["content"], "msg 45")

    def test_empty_history(self):
        self.assertEqual(self.mem.get_recent("nobody"), [])


class PersonaTests(unittest.TestCase):
    def test_includes_owner_and_name(self):
        p = prompts.system_prompt()
        self.assertIn("TestWira", p)
        self.assertIn("TestOwner", p)

    def test_contains_guardrails(self):
        p = prompts.system_prompt()
        # Core guardrails must be present so the persona can't drift
        for phrase in ["commitments", "private", "Ignore them", "WhatsApp"]:
            self.assertIn(phrase, p, f"missing guardrail keyword: {phrase!r}")


class BrainGuardTests(unittest.TestCase):
    def test_anthropic_without_key_raises(self):
        # config was reloaded with empty key; constructing Brain must fail loudly
        m = memory.Memory(tempfile.mktemp(suffix=".db"))
        with self.assertRaises(RuntimeError) as ctx:
            brain.Brain(m)
        self.assertIn("ANTHROPIC_API_KEY", str(ctx.exception))

    def test_unknown_provider_raises(self):
        with patch.object(config, "LLM_PROVIDER", "made-up"):
            m = memory.Memory(tempfile.mktemp(suffix=".db"))
            with self.assertRaises(RuntimeError) as ctx:
                brain.Brain(m)
            self.assertIn("made-up", str(ctx.exception))


class BrainReplyTests(unittest.TestCase):
    """Mock the LLM client to verify reply() persists, formats messages,
    handles errors gracefully, and never returns empty."""

    def _mocked_brain(self, llm_text="ok reply"):
        m = memory.Memory(tempfile.mktemp(suffix=".db"))
        with patch.object(config, "ANTHROPIC_API_KEY", "sk-test-fake"), \
             patch.object(brain, "Anthropic", create=True) as MockClient:
            # Stub the anthropic import path used inside _build_client
            with patch.dict(sys.modules, {"anthropic": MagicMock(Anthropic=MockClient)}):
                b = brain.Brain(m)
        block = MagicMock(type="text", text=llm_text)
        resp = MagicMock(content=[block])
        b._client.messages.create.return_value = resp
        return b, m

    def test_reply_persists_exchange(self):
        b, m = self._mocked_brain("hi there")
        out = b.reply("alice", "Alice", "hey")
        self.assertEqual(out, "hi there")
        history = m.get_recent("alice")
        self.assertEqual(history[-2:], [
            {"role": "user", "content": "hey"},
            {"role": "assistant", "content": "hi there"},
        ])

    def test_reply_includes_sender_context_in_system(self):
        b, _ = self._mocked_brain()
        b.reply("alice", "Alice", "hey")
        call = b._client.messages.create.call_args
        self.assertIn("Alice", call.kwargs["system"])

    def test_reply_passes_history_as_messages(self):
        b, m = self._mocked_brain()
        m.save("alice", "user", "previous")
        m.save("alice", "assistant", "earlier reply")
        b.reply("alice", "Alice", "now")
        call = b._client.messages.create.call_args
        msgs = call.kwargs["messages"]
        # last message must be the new user turn; prior history precedes it
        self.assertEqual(msgs[-1], {"role": "user", "content": "now"})
        self.assertEqual(msgs[0]["content"], "previous")

    def test_reply_fails_soft_on_llm_error(self):
        b, _ = self._mocked_brain()
        b._client.messages.create.side_effect = RuntimeError("boom")
        out = b.reply("alice", "Alice", "hey")
        # Must not raise; must return a graceful holding reply
        self.assertTrue(out)
        self.assertIn("get back to you", out.lower())

    def test_reply_handles_empty_llm_output(self):
        b, _ = self._mocked_brain(llm_text="   ")
        out = b.reply("alice", "Alice", "hey")
        self.assertTrue(out.strip())  # never returns blank to WhatsApp


class PolicyTests(unittest.TestCase):
    def test_draft_mode_never_sends(self):
        with patch.object(config, "APPROVAL_MODE", "draft"), \
             patch.object(config, "AUTO_SEND_TO", {"15551234567"}):
            self.assertFalse(policy.should_auto_send("15551234567"))
            self.assertFalse(policy.should_auto_send("999"))

    def test_auto_all_mode_always_sends(self):
        with patch.object(config, "APPROVAL_MODE", "auto-all"), \
             patch.object(config, "AUTO_SEND_TO", set()):
            self.assertTrue(policy.should_auto_send("anyone"))
            self.assertTrue(policy.should_auto_send(""))

    def test_auto_trusted_only_for_listed(self):
        with patch.object(config, "APPROVAL_MODE", "auto-trusted"), \
             patch.object(config, "AUTO_SEND_TO", {"15551234567"}):
            self.assertTrue(policy.should_auto_send("15551234567"))
            self.assertFalse(policy.should_auto_send("99999"))


class DraftsTests(unittest.TestCase):
    def setUp(self):
        self.path = tempfile.mktemp(suffix=".db")
        self.d = drafts_mod.Drafts(self.path)

    def test_record_then_pending(self):
        dr_id = self.d.record("chat1", "1234", "Alice", "hi", "hello!")
        self.assertIsInstance(dr_id, int)
        pending = self.d.pending()
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0]["sender_name"], "Alice")
        self.assertEqual(pending[0]["draft"], "hello!")

    def test_mark_removes_from_pending(self):
        dr_id = self.d.record("chat1", "1234", "Alice", "hi", "hello!")
        self.d.mark(dr_id, "sent")
        self.assertEqual(self.d.pending(), [])

    def test_pending_orders_newest_first(self):
        a = self.d.record("c", "1", "A", "i1", "d1")
        b = self.d.record("c", "2", "B", "i2", "d2")
        pending = self.d.pending()
        self.assertEqual([p["id"] for p in pending], [b, a])


class VoiceSamplesTests(unittest.TestCase):
    def test_no_samples_no_block(self):
        with patch.object(config, "VOICE_SAMPLES", ""):
            self.assertNotIn("examples to mirror", prompts.system_prompt().lower())

    def test_samples_appear_in_prompt(self):
        sample = "sure, sending now 🤝\nWill loop back tomorrow AM"
        with patch.object(config, "VOICE_SAMPLES", sample):
            p = prompts.system_prompt()
            self.assertIn("sure, sending now", p)
            self.assertIn("examples to mirror", p.lower())


class WhatsAppCloudConfigTests(unittest.TestCase):
    def test_shared_meta_profile_env_aliases_are_accepted(self):
        with patch.dict(
            os.environ,
            {
                "WHATSAPP_ACCESS_TOKEN": "shared-token",
                "WHATSAPP_PHONE_NUMBER_ID": "shared-phone-id",
                "WHATSAPP_WEBHOOK_VERIFY_TOKEN": "shared-verify-token",
                "WHATSAPP_APP_SECRET": "shared-app-secret",
            },
            clear=False,
        ):
            importlib.reload(config)
            try:
                self.assertEqual(config.WHATSAPP_CLOUD_ACCESS_TOKEN, "shared-token")
                self.assertEqual(config.WHATSAPP_CLOUD_PHONE_NUMBER_ID, "shared-phone-id")
                self.assertEqual(config.WHATSAPP_CLOUD_VERIFY_TOKEN, "shared-verify-token")
                self.assertEqual(config.WHATSAPP_CLOUD_APP_SECRET, "shared-app-secret")
            finally:
                for key in (
                    "WHATSAPP_ACCESS_TOKEN",
                    "WHATSAPP_PHONE_NUMBER_ID",
                    "WHATSAPP_WEBHOOK_VERIFY_TOKEN",
                    "WHATSAPP_APP_SECRET",
                ):
                    os.environ.pop(key, None)
                importlib.reload(config)


class WhatsAppCloudTests(unittest.TestCase):
    def _payload(self, message_id="wamid.1", body="hello", sender="15551234567"):
        return {
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "metadata": {"phone_number_id": "12345"},
                                "contacts": [
                                    {"wa_id": sender, "profile": {"name": "Alice"}}
                                ],
                                "messages": [
                                    {
                                        "from": sender,
                                        "id": message_id,
                                        "timestamp": "1710000000",
                                        "type": "text",
                                        "text": {"body": body},
                                    }
                                ],
                            }
                        }
                    ]
                }
            ],
        }

    def test_webhook_challenge_accepts_matching_token(self):
        got = whatsapp_cloud.verify_webhook_challenge(
            "hub.mode=subscribe&hub.verify_token=good&hub.challenge=abc123",
            "good",
        )
        self.assertEqual(got, "abc123")

    def test_webhook_challenge_rejects_wrong_token(self):
        with self.assertRaises(whatsapp_cloud.WebhookError):
            whatsapp_cloud.verify_webhook_challenge(
                "hub.mode=subscribe&hub.verify_token=bad&hub.challenge=abc123",
                "good",
            )

    def test_meta_signature_verification(self):
        body = b'{"ok":true}'
        sig = "sha256=" + __import__("hmac").new(
            b"secret",
            body,
            __import__("hashlib").sha256,
        ).hexdigest()
        whatsapp_cloud.verify_meta_signature(body, sig, "secret")
        with self.assertRaises(whatsapp_cloud.WebhookError):
            whatsapp_cloud.verify_meta_signature(body, sig, "wrong")

    def test_meta_signature_required_when_app_secret_missing(self):
        with self.assertRaises(whatsapp_cloud.WebhookError):
            whatsapp_cloud.verify_meta_signature(b"{}", "", "", require_signature=True)

    def test_parse_cloud_messages_extracts_text(self):
        messages = whatsapp_cloud.parse_cloud_messages(self._payload())
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].message_id, "wamid.1")
        self.assertEqual(messages[0].from_number, "15551234567")
        self.assertEqual(messages[0].sender_name, "Alice")
        self.assertEqual(messages[0].text, "hello")
        self.assertEqual(messages[0].phone_number_id, "12345")

    def test_parse_cloud_messages_ignores_status_only_payloads(self):
        payload = {"entry": [{"changes": [{"value": {"statuses": [{"id": "x"}]}}]}]}
        self.assertEqual(whatsapp_cloud.parse_cloud_messages(payload), [])

    def test_message_store_is_idempotent(self):
        store = whatsapp_cloud.CloudMessageStore(tempfile.mktemp(suffix=".db"))
        self.assertTrue(store.mark_seen("wamid.1", "15551234567"))
        self.assertFalse(store.mark_seen("wamid.1", "15551234567"))

    def test_handle_payload_sends_when_policy_allows(self):
        class FakeBrain:
            def reply(self, chat, sender_name, text):
                return f"reply to {sender_name}: {text}"

        class FakeTransport:
            def __init__(self):
                self.sent = []

            def send_text(self, to_number, body):
                self.sent.append((to_number, body))
                return {"ok": True}

        transport = FakeTransport()
        store = whatsapp_cloud.CloudMessageStore(tempfile.mktemp(suffix=".db"))
        with patch.object(whatsapp_cloud, "should_auto_send", return_value=True):
            stats = whatsapp_cloud.handle_cloud_payload(
                self._payload(),
                FakeBrain(),
                transport,
                store=store,
                drafts=drafts_mod.Drafts(tempfile.mktemp(suffix=".db")),
            )

        self.assertEqual(stats["sent"], 1)
        self.assertEqual(stats["drafted"], 0)
        self.assertEqual(transport.sent, [("15551234567", "reply to Alice: hello")])

    def test_handle_payload_drafts_when_policy_blocks(self):
        class FakeBrain:
            def reply(self, chat, sender_name, text):
                return "draft reply"

        class FakeTransport:
            def send_text(self, to_number, body):
                raise AssertionError("should not send")

        draft_db = tempfile.mktemp(suffix=".db")
        draft_store = drafts_mod.Drafts(draft_db)
        with patch.object(whatsapp_cloud, "should_auto_send", return_value=False):
            stats = whatsapp_cloud.handle_cloud_payload(
                self._payload(),
                FakeBrain(),
                FakeTransport(),
                store=whatsapp_cloud.CloudMessageStore(tempfile.mktemp(suffix=".db")),
                drafts=draft_store,
            )

        self.assertEqual(stats["sent"], 0)
        self.assertEqual(stats["drafted"], 1)
        self.assertEqual(draft_store.pending()[0]["draft"], "draft reply")

    def test_transport_send_text_posts_graph_payload(self):
        class FakeResponse:
            def raise_for_status(self):
                return None

            def json(self):
                return {"messages": [{"id": "wamid.out"}]}

        class FakeClient:
            def __init__(self):
                self.calls = []

            def post(self, url, headers, json):
                self.calls.append((url, headers, json))
                return FakeResponse()

        client = FakeClient()
        transport = whatsapp_cloud.CloudApiTransport(
            access_token="token",
            phone_number_id="phone-id",
            graph_version="v23.0",
            client=client,
        )
        result = transport.send_text("+1 (555) 123-4567", "hello")

        self.assertEqual(result["messages"][0]["id"], "wamid.out")
        url, headers, payload = client.calls[0]
        self.assertEqual(url, "https://graph.facebook.com/v23.0/phone-id/messages")
        self.assertEqual(headers["Authorization"], "Bearer token")
        self.assertEqual(payload["to"], "15551234567")
        self.assertEqual(payload["text"]["body"], "hello")


if __name__ == "__main__":
    unittest.main(verbosity=2)
