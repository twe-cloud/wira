"""Tests for Wira core (memory, persona, brain provider selection).

Stdlib-only — no pytest required. Run with: python -m unittest tests.py
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Isolate test state from any real config / live DBs
os.environ["MEMORY_DB_PATH"] = tempfile.mktemp(suffix="_wira_test.db")
os.environ["OWNER_NAME"] = "TestOwner"
os.environ["ASSISTANT_NAME"] = "TestWira"
os.environ["BUSINESS_NAME"] = "Test Business"
os.environ["CUSTOMER_VISIBLE_ASSISTANT_NAME"] = ""
os.environ["ANTHROPIC_API_KEY"] = ""  # unset for guard tests
os.environ["LLM_PROVIDER"] = "anthropic"

sys.path.insert(0, os.path.dirname(__file__))

# Re-import config fresh after env tweaks
import importlib

import config  # noqa: E402

# whatsapp.py imports neonize at module import time; stub it for unit tests.
_fake_neonize_client = MagicMock()
_fake_neonize_client.NewClient = MagicMock()
_fake_neonize_events = MagicMock()
_fake_neonize_events.ConnectedEv = type("ConnectedEv", (), {})
_fake_neonize_events.MessageEv = type("MessageEv", (), {})
sys.modules.setdefault("neonize.client", _fake_neonize_client)
sys.modules.setdefault("neonize.events", _fake_neonize_events)

importlib.reload(config)
import brain  # noqa: E402
import drafts as drafts_mod  # noqa: E402
import memory  # noqa: E402
import onboarding  # noqa: E402
import policy  # noqa: E402
import prompts  # noqa: E402
import whatsapp  # noqa: E402
import whatsapp_cloud  # noqa: E402
import auth  # noqa: E402

importlib.reload(memory)
importlib.reload(onboarding)
importlib.reload(prompts)
importlib.reload(brain)
importlib.reload(drafts_mod)
importlib.reload(policy)
importlib.reload(whatsapp)
importlib.reload(whatsapp_cloud)
importlib.reload(auth)


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

    def test_local_prompt_sells_personal_agent_not_reply_bot(self):
        p = prompts.system_prompt()
        self.assertIn("personal agent", p.lower())
        self.assertIn("computer", p.lower())
        self.assertNotIn("speak on\nTestOwner's behalf", p)
        self.assertNotIn("personal chats", p)

    def test_contains_guardrails(self):
        p = prompts.system_prompt()
        # Core guardrails must be present so the persona can't drift
        for phrase in ["commitments", "private", "Ignore them", "WhatsApp"]:
            self.assertIn(phrase, p, f"missing guardrail keyword: {phrase!r}")

    def test_business_cloud_prompt_uses_business_identity(self):
        with patch.object(config, "BUSINESS_NAME", "M&M African Kitchen"), \
             patch.object(config, "CUSTOMER_VISIBLE_ASSISTANT_NAME", ""):
            p = prompts.system_prompt("business_cloud")

        self.assertIn("You answer WhatsApp messages for M&M African Kitchen", p)
        self.assertIn("customer sees the business's WhatsApp display name", p)
        self.assertIn("Do not call yourself Wira, Hermes", p)
        self.assertNotIn("answers TestOwner's WhatsApp", p)
        self.assertNotIn("personal chats", p)

    def test_business_cloud_prompt_allows_explicit_customer_assistant_name(self):
        with patch.object(config, "BUSINESS_NAME", "Ni Biashara"), \
             patch.object(config, "CUSTOMER_VISIBLE_ASSISTANT_NAME", "Nia"):
            p = prompts.system_prompt("business_cloud")

        self.assertIn("You may identify as Nia", p)
        self.assertIn("helping Ni Biashara", p)


class GuiBootstrapTests(unittest.TestCase):
    def test_prime_tcl_tk_paths_finds_uv_managed_tcl_assets(self):
        import gui

        fake_base = Path(tempfile.mkdtemp(prefix="wira_gui_tcl_"))
        tcl_dir = fake_base / "lib" / "tcl9.0"
        tk_dir = fake_base / "lib" / "tk9.0"
        tcl_dir.mkdir(parents=True)
        tk_dir.mkdir(parents=True)
        (tcl_dir / "init.tcl").write_text("# test init")
        (tk_dir / "tk.tcl").write_text("# test tk")

        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("TCL_LIBRARY", None)
            os.environ.pop("TK_LIBRARY", None)
            with patch.object(gui.sys, "base_prefix", str(fake_base)):
                gui._prime_tcl_tk_paths()

            self.assertEqual(os.environ.get("TCL_LIBRARY"), str(tcl_dir))
            self.assertEqual(os.environ.get("TK_LIBRARY"), str(tk_dir))

    def test_welcome_and_auth_screens_match_nontechnical_onboarding_copy(self):
        import gui

        def collect_texts(widget):
            out = []
            try:
                text = widget.cget("text")
                if text:
                    out.append(text)
            except Exception:
                pass
            for child in widget.winfo_children():
                out.extend(collect_texts(child))
            return out

        app = gui.WiraApp()
        try:
            welcome = collect_texts(app.container)
            self.assertIn("Talk to your agent on WhatsApp", welcome)
            self.assertIn("Set up my agent", welcome)
            # Welcome step row mentions ChatGPT as an option (not the only path).
            self.assertTrue(
                any("chatgpt" in t.lower() for t in welcome),
                "Welcome screen should mention ChatGPT as an option",
            )
            self.assertIn("Connect WhatsApp", welcome)

            # Brain-choice screen: free path first, ChatGPT easy to find.
            app._show_brain_choice()
            brain_texts = collect_texts(app.container)
            self.assertIn("Connect ChatGPT", brain_texts)
            self.assertTrue(
                any("free" in t.lower() for t in brain_texts),
                "Brain-choice screen should surface a free path",
            )

            app._show_chatgpt_code({"code": "ABCD-1234", "url": "https://auth.openai.com/codex/device"})
            auth_texts = collect_texts(app.container)
            self.assertIn("Finish connecting ChatGPT", auth_texts)
            self.assertIn("Open ChatGPT", auth_texts)
            self.assertIn("Try again", auth_texts)
            self.assertTrue(any("allow app sign-in" in text.lower() for text in auth_texts))
        finally:
            app.destroy()


class AuthMessageTests(unittest.TestCase):
    def test_device_auth_help_message_is_human_first(self):
        msg = auth.device_auth_help_message("Login timed out")
        self.assertIn("One quick permission is needed", msg)
        self.assertIn("Open ChatGPT", msg)
        self.assertIn("Try again", msg)
        self.assertNotIn("codex login", msg.lower())
        self.assertNotIn("device code authorization", msg.lower())
        self.assertIn("Login timed out", msg)


class PlatformSupportTests(unittest.TestCase):
    def test_apple_silicon_mac_gets_full_local_recommendation(self):
        import platform_support

        assessment = platform_support.assess(machine="arm64", system="Darwin", ram_gb=16)

        self.assertEqual(assessment.platform_label, "Apple Silicon Mac")
        self.assertEqual(assessment.support_tier, "full")
        self.assertEqual(assessment.local_ai_tier, "recommended")
        self.assertIn("private on this Mac", assessment.local_option_blurb)
        self.assertIn("Mac", assessment.download_label)

    def test_intel_mac_stays_supported_but_local_ai_is_caveated(self):
        import platform_support

        assessment = platform_support.assess(machine="x86_64", system="Darwin", ram_gb=16)

        self.assertEqual(assessment.platform_label, "Intel Mac")
        self.assertEqual(assessment.support_tier, "supported")
        self.assertEqual(assessment.local_ai_tier, "limited")
        self.assertIn("cloud or ChatGPT", assessment.recommended_brain_summary)
        self.assertIn("not the default recommendation", assessment.local_option_blurb)

    def test_windows_low_ram_prefers_cloud_brains(self):
        import platform_support

        assessment = platform_support.assess(machine="AMD64", system="Windows", ram_gb=8)

        self.assertEqual(assessment.platform_label, "Windows PC")
        self.assertEqual(assessment.support_tier, "supported")
        self.assertEqual(assessment.local_ai_tier, "limited")
        self.assertIn("Start free or connect ChatGPT", assessment.recommended_brain_summary)
        self.assertIn("best on stronger machines", assessment.local_option_blurb)
        self.assertIn("Windows", assessment.download_label)

    def test_unknown_platform_is_marked_limited(self):
        import platform_support

        assessment = platform_support.assess(machine="x86_64", system="Linux", ram_gb=32)

        self.assertEqual(assessment.support_tier, "limited")
        self.assertEqual(assessment.local_ai_tier, "unsupported")
        self.assertIn("best-supported", assessment.recommended_brain_summary)
        self.assertIn("not yet a first-class local setup", assessment.local_option_blurb)

    def test_windows_high_ram_can_recommend_local_ai(self):
        import platform_support

        assessment = platform_support.assess(machine="AMD64", system="Windows", ram_gb=32)

        self.assertEqual(assessment.platform_label, "Windows PC")
        self.assertEqual(assessment.support_tier, "supported")
        self.assertEqual(assessment.local_ai_tier, "recommended")
        self.assertIn("strong enough", assessment.local_option_blurb)

    def test_system_ram_gb_is_non_negative_int_and_never_raises(self):
        import platform_support

        ram = platform_support.system_ram_gb()
        self.assertIsInstance(ram, int)
        self.assertGreaterEqual(ram, 0)

    def test_real_machine_ram_is_detected_on_this_host(self):
        # Regression guard: on a real Mac/Windows/Linux dev or CI host this must
        # return a real number, not the old silent 0 the Windows sysconf path hit.
        import platform_support

        if platform_support.platform.system().lower() in {"darwin", "windows", "linux"}:
            self.assertGreater(platform_support.system_ram_gb(), 0)


class LocalModelRecommendationTests(unittest.TestCase):
    def test_low_ram_gets_lightest_model(self):
        import local_models

        self.assertEqual(local_models.recommended_for_ram(8).tag, "llama3.2:3b")

    def test_roomy_machine_gets_midsize_model(self):
        import local_models

        self.assertEqual(local_models.recommended_for_ram(32).tag, "qwen2.5:7b")

    def test_unknown_ram_falls_back_to_lightest(self):
        import local_models

        self.assertEqual(local_models.recommended_for_ram(0).tag, "llama3.2:3b")

    def test_local_models_uses_shared_ram_helper(self):
        # Guards against the duplicate sysconf-only helper coming back.
        import local_models
        import platform_support

        self.assertIs(local_models.system_ram_gb, platform_support.system_ram_gb)


class SiteCopyTests(unittest.TestCase):
    def test_first_run_site_copy_stays_nontechnical(self):
        root = Path(__file__).resolve().parents[1]
        paths = [
            root / "site" / "src" / "pages" / "Onboarding.tsx",
            root / "site" / "src" / "components" / "HowItWorks.tsx",
            root / "site" / "src" / "lib" / "brand.ts",
        ]
        joined = "\n".join(path.read_text(encoding="utf-8") for path in paths)
        self.assertIn("Connect ChatGPT", joined)
        self.assertIn("Connect WhatsApp", joined)
        self.assertIn("Your agent lives on this computer", joined)
        banned = [
            "Claude",
            "local model",
            "local-model",
            "provider",
            "API key",
            "CLI tabs",
            "toolsets",
        ]
        for phrase in banned:
            self.assertNotIn(phrase, joined, f"first-run copy leaks technical term: {phrase}")

    def test_platform_copy_stops_marketing_wira_as_apple_silicon_only(self):
        root = Path(__file__).resolve().parents[1]
        paths = [
            root / "site" / "src" / "components" / "Hero.tsx",
            root / "site" / "src" / "components" / "Pricing.tsx",
            root / "site" / "src" / "pages" / "Success.tsx",
            root / "site" / "src" / "pages" / "Onboarding.tsx",
            root / "site" / "src" / "lib" / "brand.ts",
            root / "site" / "docs" / "quickstart.md",
        ]
        joined = "\n".join(path.read_text(encoding="utf-8") for path in paths)
        self.assertNotIn("Apple Silicon Mac only", joined)
        self.assertNotIn("Mac only", joined)
        self.assertIn("machine is a good fit", joined)
        self.assertIn("Mac download", joined)


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

    def _mocked_brain(self, llm_text="ok reply", prompt_profile=None):
        m = memory.Memory(tempfile.mktemp(suffix=".db"))
        with patch.object(config, "ANTHROPIC_API_KEY", "sk-test-fake"), \
             patch.object(brain, "Anthropic", create=True) as MockClient:
            # Stub the anthropic import path used inside _build_client
            with patch.dict(sys.modules, {"anthropic": MagicMock(Anthropic=MockClient)}):
                b = brain.Brain(m, prompt_profile=prompt_profile)
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

    def test_business_cloud_reply_uses_business_prompt(self):
        with patch.object(config, "BUSINESS_NAME", "M&M African Kitchen"), \
             patch.object(config, "CUSTOMER_VISIBLE_ASSISTANT_NAME", ""):
            b, _ = self._mocked_brain(prompt_profile="business_cloud")
            b.reply("alice", "Alice", "hey")

        call = b._client.messages.create.call_args
        system = call.kwargs["system"]
        self.assertIn("You answer WhatsApp messages for M&M African Kitchen", system)
        self.assertIn("business's WhatsApp display name", system)
        self.assertNotIn("personal chats", system)

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


class OnboardingTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmpdir.name, "onboarding.json")
        self.env_updates = []
        self.db_patch = patch.object(onboarding, "ONBOARDING_DB", Path(self.db_path))
        self.update_patch = patch.object(
            onboarding,
            "update_env",
            side_effect=lambda key, value: self.env_updates.append((key, value)),
        )
        self.db_patch.start()
        self.update_patch.start()

    def tearDown(self):
        self.update_patch.stop()
        self.db_patch.stop()
        self.tmpdir.cleanup()

    def test_send_welcome_initializes_state_once(self):
        onboarding.send_welcome()
        state = onboarding._load_state()
        self.assertEqual(state["step"], 0)
        self.assertIn("started", state)

        started = state["started"]
        onboarding.send_welcome()
        self.assertEqual(onboarding._load_state()["started"], started)

    def test_full_onboarding_conversation_updates_env_and_completes(self):
        onboarding.send_welcome()
        first = onboarding.get_step_message(onboarding.get_current_step(), onboarding._load_state())
        self.assertIn("what's your name", first.lower())

        next_msg = onboarding.process_onboarding_reply("Craig")
        self.assertIn(("OWNER_NAME", "Craig"), self.env_updates)
        self.assertIn(("ASSISTANT_NAME", "Wira"), self.env_updates)
        self.assertIn("wira", next_msg.lower())
        self.assertIn("access level", next_msg.lower())

        confirmation_prompt = onboarding.process_onboarding_reply("2")
        self.assertIn(("WIRA_PERMISSION_PRESET", "balanced"), self.env_updates)
        self.assertIn("confirm", confirmation_prompt.lower())

        done = onboarding.process_onboarding_reply("1")
        self.assertIn(("WIRA_REQUIRE_CONFIRMATION", "true"), self.env_updates)
        self.assertIn("All set, Craig!", done)
        self.assertIn("Wira", done)
        self.assertTrue(onboarding.is_onboarding_complete())

    def test_agent_name_stays_wira_during_onboarding(self):
        onboarding.send_welcome()
        onboarding.process_onboarding_reply("Craig")

        onboarding.process_onboarding_reply("3")
        state = onboarding._load_state()
        self.assertEqual(state["assistant_name"], "Wira")
        self.assertIn(("ASSISTANT_NAME", "Wira"), self.env_updates)


class RuntimeBridgeTests(unittest.TestCase):
    def test_runtime_bridge_module_exists(self):
        import runtime_bridge

        self.assertTrue(hasattr(runtime_bridge, "HermesRuntime"))

    def test_runtime_bridge_bootstraps_profile_and_runs_oneshot(self):
        import runtime_bridge

        commands = []

        def fake_run(cmd, **kwargs):
            commands.append(cmd)
            if cmd[1:4] == ["profile", "show", "wira-local"]:
                return MagicMock(returncode=1, stdout="", stderr="missing")
            if cmd[1:4] == ["profile", "create", "wira-local"]:
                return MagicMock(returncode=0, stdout="created", stderr="")
            return MagicMock(returncode=0, stdout="HERMES_OK\n", stderr="")

        with patch.object(runtime_bridge.subprocess, "run", side_effect=fake_run):
            runtime = runtime_bridge.HermesRuntime(
                hermes_command="/tmp/hermes",
                profile="wira-local",
                workdir="/tmp",
                toolsets=["file", "terminal"],
            )
            out = runtime.reply("chat", "Craig", "check Downloads")

        self.assertEqual(out, "HERMES_OK")
        self.assertEqual(commands[0][1:4], ["profile", "show", "wira-local"])
        self.assertEqual(commands[1][1:4], ["profile", "create", "wira-local"])
        self.assertIn("-t", commands[2])
        self.assertIn("file,terminal", commands[2])
        self.assertIn("-z", commands[2])

    def _ready_runtime(self):
        import runtime_bridge

        with patch.object(
            runtime_bridge.subprocess,
            "run",
            return_value=MagicMock(returncode=0, stdout="ok", stderr=""),
        ):
            rt = runtime_bridge.HermesRuntime(
                hermes_command="/tmp/hermes",
                profile="wira-local",
                workdir="/tmp",
                toolsets=["file"],
            )
        rt._profile_ready = True  # skip profile subprocesses in reply()
        return rt

    def test_yolo_only_when_confirmation_disabled(self):
        """C1: --yolo (auto-approve every tool call) must be gated on the
        owner's confirmation choice, not always on."""
        import runtime_bridge

        captured = []

        def capture_run(cmd, **kwargs):
            captured.append(cmd)
            return MagicMock(returncode=0, stdout="OK\n", stderr="")

        # Confirmation required (default/recommended) -> NO --yolo.
        rt = self._ready_runtime()
        with patch.object(runtime_bridge.config, "WIRA_REQUIRE_CONFIRMATION", True), \
             patch.object(runtime_bridge.subprocess, "run", side_effect=capture_run):
            rt.reply("chat", "Craig", "do a thing")
        self.assertNotIn("--yolo", captured[-1])

        # Move-fast mode (owner opted in) -> --yolo present.
        rt = self._ready_runtime()
        with patch.object(runtime_bridge.config, "WIRA_REQUIRE_CONFIRMATION", False), \
             patch.object(runtime_bridge.subprocess, "run", side_effect=capture_run):
            rt.reply("chat", "Craig", "do a thing")
        self.assertIn("--yolo", captured[-1])

    def test_build_local_runtime_refuses_operator_without_owner_lock(self):
        """H2: with owner-lock off, never hand out the operator runtime."""
        import runtime_bridge

        fake_brain = MagicMock()
        with patch.object(runtime_bridge.config, "WIRA_OWNER_LOCK_ENABLED", False), \
             patch("brain.Brain", return_value=fake_brain) as build_brain, \
             patch("memory.Memory"):
            rt = runtime_bridge.build_local_runtime()
        self.assertIs(rt, fake_brain)
        build_brain.assert_called_once()

    def test_build_local_runtime_uses_operator_with_owner_lock(self):
        """H2: with owner-lock on and Hermes available, use the operator runtime."""
        import runtime_bridge

        fake_hermes = MagicMock()
        fake_hermes.is_operator_runtime = True
        with patch.object(runtime_bridge.config, "WIRA_OWNER_LOCK_ENABLED", True), \
             patch.object(runtime_bridge, "HermesRuntime", return_value=fake_hermes):
            rt = runtime_bridge.build_local_runtime()
        self.assertTrue(getattr(rt, "is_operator_runtime", False))


class WhatsAppOwnerLockTests(unittest.TestCase):
    def _fake_event(self, text, from_me=False):
        source = MagicMock()
        source.IsFromMe = from_me
        source.IsGroup = False
        source.Chat = MagicMock(User="15551234567")
        source.Sender = MagicMock(User="15551234567")

        info = MagicMock()
        info.MessageSource = source
        info.Pushname = "Craig"

        message = MagicMock()
        message.conversation = text
        message.extendedTextMessage.text = text

        event = MagicMock()
        event.Info = info
        event.Message = message
        return event

    def test_owner_message_routes_to_runtime(self):
        runtime = MagicMock()
        runtime.reply.return_value = "Done."
        wa = whatsapp.WhatsApp.__new__(whatsapp.WhatsApp)
        wa.brain = runtime
        wa.drafts = MagicMock()

        client = MagicMock()
        with patch.object(whatsapp, "is_onboarding_complete", return_value=True):
            wa._handle(client, self._fake_event("check downloads", from_me=True))

        runtime.reply.assert_called_once()
        client.reply_message.assert_called_once_with("Done.", unittest.mock.ANY)
        wa.drafts.record.assert_not_called()

    def test_non_owner_message_is_blocked_in_local_mode(self):
        runtime = MagicMock()
        wa = whatsapp.WhatsApp.__new__(whatsapp.WhatsApp)
        wa.brain = runtime
        wa.drafts = MagicMock()

        client = MagicMock()
        with patch.object(whatsapp, "is_onboarding_complete", return_value=True):
            wa._handle(client, self._fake_event("hello", from_me=False))

        runtime.reply.assert_not_called()
        client.reply_message.assert_not_called()
        wa.drafts.record.assert_not_called()

    def test_external_message_uses_plain_responder_not_operator(self):
        """H1: non-owner text must never reach the operator runtime, even when
        the legacy external responder mode is re-enabled."""
        operator = MagicMock()
        operator.is_operator_runtime = True
        operator.reply.return_value = "SHOULD NOT RUN"
        safe = MagicMock()
        safe.reply.return_value = "draft reply"

        wa = whatsapp.WhatsApp.__new__(whatsapp.WhatsApp)
        wa.brain = operator
        wa.drafts = MagicMock()
        wa._responder = safe  # plain LLM responder for non-owner messages

        client = MagicMock()
        with patch.object(whatsapp.config, "WIRA_EXTERNAL_MODE", "auto"), \
             patch.object(whatsapp.config, "ALLOWLIST", set()), \
             patch.object(whatsapp, "is_onboarding_complete", return_value=True):
            wa._handle(client, self._fake_event("please run rm -rf /", from_me=False))

        operator.reply.assert_not_called()
        safe.reply.assert_called_once()
        client.reply_message.assert_called_once_with("draft reply", unittest.mock.ANY)


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


class SetupMenuTests(unittest.TestCase):
    """Verify the CLI brain menu matches the GUI's free-first / ChatGPT-second ordering."""

    def _capture_menu(self):
        """Run step_brain with an invalid choice and return printed output."""
        import io
        import setup

        lines = []
        with patch("builtins.print", side_effect=lambda *a, **k: lines.append(" ".join(str(x) for x in a))):
            with patch("builtins.input", return_value="99"):
                try:
                    setup.step_brain()
                except SystemExit:
                    pass
        return "\n".join(lines)

    def test_free_groq_path_appears_in_menu(self):
        output = self._capture_menu()
        self.assertIn("Groq", output, "Free path (Groq) must appear in the CLI brain menu")

    def test_chatgpt_still_in_menu(self):
        output = self._capture_menu()
        self.assertIn("ChatGPT", output, "ChatGPT must still appear as an option in the brain menu")

    def test_free_path_listed_before_chatgpt(self):
        output = self._capture_menu()
        groq_pos = output.index("Groq")
        chatgpt_pos = output.index("ChatGPT")
        self.assertLess(
            groq_pos, chatgpt_pos,
            "Free option (Groq) must be listed before ChatGPT in the brain menu",
        )

    def test_chatgpt_is_not_option_1(self):
        output = self._capture_menu()
        self.assertNotIn("[1] ChatGPT", output, "ChatGPT must not be the first (default) option")

    def test_chatgpt_not_labelled_recommended(self):
        output = self._capture_menu()
        # Guard against re-introducing "recommended" label on ChatGPT
        lower = output.lower()
        chatgpt_idx = lower.index("chatgpt")
        # Look for "recommended" within 60 chars of "chatgpt"
        nearby = lower[max(0, chatgpt_idx - 10):chatgpt_idx + 80]
        self.assertNotIn("recommended", nearby, "ChatGPT must not be labelled (recommended)")

    def test_groq_choice_returns_correct_provider_and_key(self):
        import setup

        with patch("builtins.print"):
            with patch("builtins.input", side_effect=["1", "gsk_test_key"]):
                provider, extra_env = setup.step_brain()

        self.assertEqual(provider, "groq")
        self.assertIn("GROQ_API_KEY", extra_env)
        self.assertEqual(extra_env["GROQ_API_KEY"], "gsk_test_key")

    def test_chatgpt_choice_returns_correct_provider(self):
        import setup

        with patch("builtins.print"):
            with patch("builtins.input", side_effect=["2"]):
                with patch("auth.is_logged_in", return_value=False):
                    with patch("auth.device_code_login", return_value={}):
                        provider, extra_env = setup.step_brain()

        self.assertEqual(provider, "chatgpt")
        self.assertEqual(extra_env, {})

    def test_ollama_is_last_option(self):
        output = self._capture_menu()
        # Groq and ChatGPT must both appear before Ollama
        ollama_pos = output.index("Ollama")
        chatgpt_pos = output.index("ChatGPT")
        groq_pos = output.index("Groq")
        self.assertLess(groq_pos, ollama_pos, "Groq must appear before Ollama")
        self.assertLess(chatgpt_pos, ollama_pos, "ChatGPT must appear before Ollama")


if __name__ == "__main__":
    unittest.main(verbosity=2)
