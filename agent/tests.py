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

importlib.reload(memory)
importlib.reload(prompts)
importlib.reload(brain)
importlib.reload(drafts_mod)
importlib.reload(policy)


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


if __name__ == "__main__":
    unittest.main(verbosity=2)
