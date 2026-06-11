#!/usr/bin/env python3
"""Wira — visual setup wizard and background agent.

The product promise is simple:
1. Wira runs on this computer.
2. The buyer can start free, use ChatGPT, or keep it private when the machine is a good fit.
3. It brings their agent to WhatsApp as fast as possible.

After setup, Wira keeps the local runtime available in the background.
"""

import logging
import os
import queue
import sys
import threading
from io import BytesIO
from pathlib import Path


def _prime_tcl_tk_paths() -> None:
    """Help uv-managed Python builds find bundled Tcl/Tk assets.

    On this machine the Hermes venv uses a uv-installed CPython whose Tcl/Tk
    libraries live under ``sys.base_prefix/lib`` rather than the traditional
    venv-relative lookup paths Tk expects. Importing ``tkinter`` works, but
    constructing ``tk.Tk()`` fails unless ``TCL_LIBRARY`` / ``TK_LIBRARY`` are
    pointed at the real asset directories.
    """
    if os.environ.get("TCL_LIBRARY") and os.environ.get("TK_LIBRARY"):
        return

    base_prefix = Path(getattr(sys, "base_prefix", sys.prefix))
    candidates = [
        (base_prefix / "lib" / "tcl9.0", base_prefix / "lib" / "tk9.0"),
        (base_prefix / "lib" / "tcl8.6", base_prefix / "lib" / "tk8.6"),
        (base_prefix / "Library" / "lib" / "tcl8.6", base_prefix / "Library" / "lib" / "tk8.6"),
    ]

    for tcl_dir, tk_dir in candidates:
        if not os.environ.get("TCL_LIBRARY") and (tcl_dir / "init.tcl").exists():
            os.environ["TCL_LIBRARY"] = str(tcl_dir)
        if not os.environ.get("TK_LIBRARY") and (tk_dir / "tk.tcl").exists():
            os.environ["TK_LIBRARY"] = str(tk_dir)
        if os.environ.get("TCL_LIBRARY") and os.environ.get("TK_LIBRARY"):
            return


_prime_tcl_tk_paths()

import tkinter as tk

from paths import ENV_FILE, RELEASES_URL, SESSION_DB_PATH, load_env, write_env
import platform_support

# Load user-owned config before anything else.
load_env()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("wira.gui")
PLATFORM = platform_support.assess()

# Brand colors — warmer and more business-grade than the old green utility skin.
BG = "#0d1422"
BG_SOFT = "#162238"
PANEL_BG = "#f4eee3"
PANEL_ALT = "#ebe2d2"
PANEL_EDGE = "#d8cab1"
ACCENT = "#9f7a2f"
ACCENT_DARK = "#6f5318"
ACCENT_LIGHT = "#d6b268"
TEXT = "#1a2233"
TEXT_DIM = "#5f6472"
TEXT_SOFT = "#8d7550"
WHITE = "#ffffff"
SUCCESS = "#35624d"
ERROR = "#9a3f2f"

FONT_TITLE = ("Avenir Next", 30, "bold")
FONT_HEADING = ("Avenir Next", 20, "bold")
FONT_BODY = ("Avenir Next", 14)
FONT_SMALL = ("Avenir Next", 12)
FONT_EYEBROW = ("Avenir Next", 11, "bold")
FONT_CODE = ("Menlo", 24, "bold")
FONT_MONO = ("Menlo", 12)

WIN_W, WIN_H = 560, 700


class WiraApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Wira")
        self.geometry(f"{WIN_W}x{WIN_H}")
        self.configure(bg=BG)
        self.resizable(False, False)

        # Event queues for cross-thread communication
        self.event_queue = queue.Queue()

        # State
        self._chatgpt_token = None
        self._qr_photo = None  # prevent GC

        # Container for screens
        self.container = tk.Frame(self, bg=BG)
        self.container.pack(fill="both", expand=True, padx=40, pady=30)

        # Check if already set up
        from auth import is_logged_in
        if is_logged_in() and SESSION_DB_PATH.exists() and SESSION_DB_PATH.stat().st_size > 0:
            self._show_running()
        else:
            self._show_welcome()

        # Poll event queue
        self.after(100, self._poll_events)

    def _clear(self):
        for w in self.container.winfo_children():
            w.destroy()

    def _panel(self):
        panel = tk.Frame(
            self.container,
            bg=PANEL_BG,
            highlightbackground=PANEL_EDGE,
            highlightthickness=1,
            bd=0,
            padx=28,
            pady=24,
        )
        panel.pack(fill="both", expand=True, padx=8, pady=10)
        return panel

    def _eyebrow(self, parent, text):
        tk.Label(
            parent,
            text=text.upper(),
            font=FONT_EYEBROW,
            fg=TEXT_SOFT,
            bg=PANEL_BG,
            anchor="w",
        ).pack(fill="x", pady=(0, 10))

    def _headline(self, parent, text):
        tk.Label(
            parent,
            text=text,
            font=FONT_TITLE,
            fg=TEXT,
            bg=PANEL_BG,
            justify="left",
            anchor="w",
            wraplength=460,
        ).pack(fill="x", pady=(0, 10))

    def _body(self, parent, text, *, small=False, fg=None, center=False, pady=(0, 12)):
        tk.Label(
            parent,
            text=text,
            font=FONT_SMALL if small else FONT_BODY,
            fg=fg or TEXT_DIM,
            bg=PANEL_BG,
            justify="center" if center else "left",
            anchor="center" if center else "w",
            wraplength=460,
        ).pack(fill="x", pady=pady)

    def _bullet_row(self, parent, title, body):
        row = tk.Frame(parent, bg=PANEL_ALT, padx=14, pady=12)
        row.pack(fill="x", pady=6)
        dot = tk.Canvas(row, width=14, height=14, bg=PANEL_ALT, highlightthickness=0)
        dot.create_oval(2, 2, 12, 12, fill=ACCENT, outline=ACCENT)
        dot.pack(side="left", padx=(0, 10), pady=3)
        text_col = tk.Frame(row, bg=PANEL_ALT)
        text_col.pack(side="left", fill="x", expand=True)
        tk.Label(text_col, text=title, font=("Avenir Next", 13, "bold"), fg=TEXT, bg=PANEL_ALT, anchor="w").pack(fill="x")
        tk.Label(text_col, text=body, font=FONT_SMALL, fg=TEXT_DIM, bg=PANEL_ALT, anchor="w", justify="left", wraplength=390).pack(fill="x", pady=(2, 0))

    def _step_row(self, parent, number, title, body):
        row = tk.Frame(parent, bg=PANEL_ALT, padx=14, pady=12)
        row.pack(fill="x", pady=6)
        badge = tk.Label(row, text=str(number), font=("Avenir Next", 13, "bold"), fg=WHITE, bg=ACCENT_DARK, width=2)
        badge.pack(side="left", padx=(0, 12), pady=2)
        text_col = tk.Frame(row, bg=PANEL_ALT)
        text_col.pack(side="left", fill="x", expand=True)
        tk.Label(text_col, text=title, font=("Avenir Next", 13, "bold"), fg=TEXT, bg=PANEL_ALT, anchor="w").pack(fill="x")
        tk.Label(text_col, text=body, font=FONT_SMALL, fg=TEXT_DIM, bg=PANEL_ALT, anchor="w", justify="left", wraplength=390).pack(fill="x", pady=(2, 0))

    def _primary_button(self, parent, text, command, *, pady=(10, 0)):
        btn = tk.Button(
            parent,
            text=text,
            font=("Avenir Next", 14, "bold"),
            fg=WHITE,
            bg=ACCENT_DARK,
            activebackground=ACCENT,
            activeforeground=WHITE,
            relief="flat",
            bd=0,
            padx=20,
            pady=12,
            cursor="hand2",
            command=command,
        )
        btn.pack(fill="x", pady=pady)
        return btn

    def _secondary_button(self, parent, text, command, *, pady=(10, 0)):
        btn = tk.Button(
            parent,
            text=text,
            font=FONT_BODY,
            fg=TEXT,
            bg=PANEL_ALT,
            activebackground=PANEL_EDGE,
            activeforeground=TEXT,
            relief="flat",
            bd=0,
            padx=20,
            pady=10,
            cursor="hand2",
            command=command,
        )
        btn.pack(fill="x", pady=pady)
        return btn

    def _poll_events(self):
        try:
            while True:
                event_type, data = self.event_queue.get_nowait()
                if event_type == "brain_detect":
                    self._render_brain_detection(data)
                elif event_type == "local_progress":
                    self._render_local_progress(data)
                elif event_type == "local_done":
                    self._show_whatsapp()
                elif event_type == "local_error":
                    self._show_local_error(data)
                elif event_type == "provider_result":
                    self._render_provider_result(data)
                elif event_type == "chatgpt_code":
                    self._show_chatgpt_code(data)
                elif event_type == "chatgpt_done":
                    self._chatgpt_token = data
                    self._show_whatsapp()
                elif event_type == "chatgpt_error":
                    self._show_chatgpt_error(data)
                elif event_type == "qr":
                    self._render_qr(data)
                elif event_type == "connected":
                    self._show_live()
                elif event_type == "error":
                    self._show_error(data)
        except queue.Empty:
            pass
        self.after(100, self._poll_events)

    # ─── Screen: Welcome ───────────────────────────────────────

    def _show_welcome(self):
        self._clear()
        f = self._panel()

        self._eyebrow(f, "Wira")
        self._headline(f, "Talk to your agent on WhatsApp")
        self._body(
            f,
            "Wira sets up a personal agent on this computer and brings it to WhatsApp as fast as possible.",
            pady=(0, 18),
        )
        self._body(f, PLATFORM.welcome_blurb, fg=TEXT_SOFT, small=True, pady=(0, 18))

        self._bullet_row(f, "Start free in under a minute", "Pick a free brain — like Groq — or connect your ChatGPT subscription.")
        self._bullet_row(f, "Your agent lives on this computer", "That is what lets it do real work for you instead of acting like a toy chat window.")
        self._bullet_row(f, "Talk on WhatsApp", "Your phone becomes the easiest way to reach your agent while the actual work happens here.")

        self._body(f, "Setup takes two steps.", fg=TEXT, small=True, pady=(20, 8))
        self._step_row(f, 1, "Choose your agent's brain", PLATFORM.recommended_brain_summary)
        self._step_row(f, 2, "Connect WhatsApp", "Scan one code so you can start texting your agent immediately.")

        self._primary_button(f, "Set up my agent", self._show_brain_choice, pady=(22, 0))

    # ─── Screen: Choose the brain ──────────────────────────────

    def _show_brain_choice(self):
        """Let the buyer pick how their agent thinks.

        Order: free API path first (fastest start), ChatGPT subscription
        second (easy, use what you have), local/Ollama third (private but
        requires extra setup).
        """
        self._clear()
        f = self._panel()

        self._eyebrow(f, "Step 1 of 2")
        self._headline(f, "Choose your agent's brain")
        self._body(
            f,
            f"Pick the fastest way to get started on this {PLATFORM.platform_label.lower()}. You can always change this later.",
            pady=(0, 16),
        )

        # ── Free API path — fastest start, shown first ──────────
        import providers as _providers
        key_card = tk.Frame(f, bg=PANEL_ALT, padx=16, pady=14)
        key_card.pack(fill="x", pady=(0, 10))
        tk.Label(
            key_card, text="FREE · FASTEST START", font=FONT_EYEBROW,
            fg=ACCENT_DARK, bg=PANEL_ALT, anchor="w",
        ).pack(fill="x")
        tk.Label(
            key_card, text="Start free with an API key", font=("Avenir Next", 16, "bold"),
            fg=TEXT, bg=PANEL_ALT, anchor="w",
        ).pack(fill="x", pady=(2, 2))
        tk.Label(
            key_card,
            text="Groq has a generous free tier. Or pick another provider and paste a key.",
            font=FONT_SMALL, fg=TEXT_DIM, bg=PANEL_ALT, anchor="w",
            justify="left", wraplength=420,
        ).pack(fill="x", pady=(0, 8))
        btn_row = tk.Frame(key_card, bg=PANEL_ALT)
        btn_row.pack(fill="x")
        for pid in _providers.ONBOARDING_PRESETS:
            p = _providers.preset(pid)
            tk.Button(
                btn_row, text=p["label"], font=FONT_SMALL, fg=TEXT, bg=PANEL_BG,
                activebackground=PANEL_EDGE, relief="flat", bd=0, padx=14, pady=8,
                cursor="hand2", command=lambda i=pid: self._show_api_provider(i),
            ).pack(side="left", padx=(0, 8))
        self._secondary_button(key_card, "See all providers", self._show_all_providers, pady=(10, 0))

        # ── ChatGPT subscription — easy, familiar ───────────────
        cg = tk.Frame(f, bg=PANEL_ALT, padx=16, pady=14)
        cg.pack(fill="x", pady=(0, 10))
        tk.Label(
            cg, text="EASY · USE WHAT YOU HAVE", font=FONT_EYEBROW,
            fg=ACCENT_DARK, bg=PANEL_ALT, anchor="w",
        ).pack(fill="x")
        tk.Label(
            cg, text="Use my ChatGPT subscription", font=("Avenir Next", 16, "bold"),
            fg=TEXT, bg=PANEL_ALT, anchor="w",
        ).pack(fill="x", pady=(2, 2))
        tk.Label(
            cg,
            text="Connect the ChatGPT account you already pay for. One sign-in and you're done.",
            font=FONT_SMALL, fg=TEXT_DIM, bg=PANEL_ALT, anchor="w",
            justify="left", wraplength=420,
        ).pack(fill="x", pady=(0, 8))
        self._primary_button(cg, "Connect ChatGPT", self._start_chatgpt_login, pady=(0, 0))

        # ── Local / Ollama — private, optional ──────────────────
        self._local_card = tk.Frame(f, bg=PANEL_ALT, padx=16, pady=14)
        self._local_card.pack(fill="x", pady=(0, 6))
        tk.Label(
            self._local_card, text="PRIVATE · LOCAL AI", font=FONT_EYEBROW,
            fg=TEXT_SOFT, bg=PANEL_ALT, anchor="w",
        ).pack(fill="x")
        tk.Label(
            self._local_card, text="Run it locally with Ollama", font=("Avenir Next", 16, "bold"),
            fg=TEXT, bg=PANEL_ALT, anchor="w",
        ).pack(fill="x", pady=(2, 2))
        tk.Label(
            self._local_card,
            text=PLATFORM.local_option_blurb,
            font=FONT_SMALL, fg=TEXT_DIM, bg=PANEL_ALT, anchor="w",
            justify="left", wraplength=420,
        ).pack(fill="x")
        self._local_status = tk.Label(
            self._local_card, text=f"Checking this {PLATFORM.platform_label.lower()}…", font=FONT_SMALL,
            fg=TEXT_SOFT, bg=PANEL_ALT, anchor="w", justify="left", wraplength=420,
        )
        self._local_status.pack(fill="x", pady=(8, 6))
        self._local_action = tk.Frame(self._local_card, bg=PANEL_ALT)
        self._local_action.pack(fill="x")

        # Kick off local detection without blocking the UI.
        threading.Thread(target=self._brain_detect_thread, daemon=True).start()

    def _brain_detect_thread(self):
        try:
            import local_models
            self.event_queue.put(("brain_detect", local_models.detect()))
        except Exception as e:
            logger.warning("Local-brain detection failed: %s", e)
            self.event_queue.put(("brain_detect", None))

    def _render_brain_detection(self, detection):
        if not hasattr(self, "_local_status") or not self._local_status.winfo_exists():
            return
        import local_models
        for w in self._local_action.winfo_children():
            w.destroy()

        if PLATFORM.local_ai_tier == "unsupported":
            self._local_status.config(text=PLATFORM.local_option_blurb)
            self._secondary_button(
                self._local_action,
                "Use the fastest supported setup instead",
                self._show_all_providers,
                pady=(0, 0),
            )
            return

        if detection is None or not detection.installed:
            self._local_status.config(
                text=f"Local AI (Ollama) isn't installed yet. Install it once, then Wira can use the private local-AI lane on this {PLATFORM.platform_label.lower()}."
            )
            self._primary_button(self._local_action, "Get local AI (Ollama)",
                                 lambda: self._open_url(local_models.ollama_download_url()), pady=(0, 6))
            self._secondary_button(self._local_action, "I installed it — check again",
                                   self._show_brain_choice, pady=(0, 0))
            return

        if not detection.running:
            self._local_status.config(
                text="Ollama is installed but not running. Open the Ollama app, then "
                     "check again."
            )
            self._secondary_button(self._local_action, "Check again",
                                   self._show_brain_choice, pady=(0, 0))
            return

        rec = detection.recommended
        ram = f"{detection.ram_gb} GB" if detection.ram_gb else "your"
        already = detection.has_recommended
        self._local_status.config(
            text=(f"Ready. Recommended model for {ram} RAM: {rec.name} ({rec.size_label}). "
                  f"{rec.note}")
            + ("" if already else "\nWira will download it once, then run it locally forever.")
        )
        label = f"Use {rec.name} locally" if already else f"Download {rec.name} & go"
        self._primary_button(
            self._local_action, label,
            lambda t=rec.tag: self._choose_local(t), pady=(0, 0),
        )

    def _choose_local(self, tag: str):
        self._clear()
        f = self._panel()
        self._eyebrow(f, "Step 1 of 2")
        self._headline(f, "Setting up your local brain")
        self._body(
            f,
            PLATFORM.local_setup_blurb,
            pady=(0, 18),
        )
        self._local_progress_label = tk.Label(
            f, text="Starting…", font=FONT_BODY, fg=TEXT_SOFT, bg=PANEL_BG,
            justify="left", anchor="w", wraplength=440,
        )
        self._local_progress_label.pack(fill="x", pady=(6, 0))
        threading.Thread(target=self._local_setup_thread, args=(tag,), daemon=True).start()

    def _local_setup_thread(self, tag: str):
        try:
            import local_models

            if tag not in local_models.installed_models():
                def _cb(status, completed, total):
                    pct = f" {completed * 100 // total}%" if total else ""
                    self.event_queue.put(("local_progress", f"{status}{pct}"))
                ok = local_models.pull_model(tag, _cb)
                if not ok:
                    self.event_queue.put((
                        "local_error",
                        "The model download didn't finish. Check your internet "
                        "connection and the Ollama app, then try again.",
                    ))
                    return

            self.event_queue.put(("local_progress", "Testing the model…"))
            if not local_models.smoke_test(tag):
                self.event_queue.put((
                    "local_error",
                    "The local model is installed but didn't respond to a test "
                    "message. Make sure the Ollama app is running, then try again.",
                ))
                return

            self._ensure_env()
            local_models.select_local_brain(tag)
            self.event_queue.put(("local_done", None))
        except Exception as e:
            logger.exception("Local setup error")
            self.event_queue.put(("local_error", str(e)))

    def _render_local_progress(self, text: str):
        if hasattr(self, "_local_progress_label") and self._local_progress_label.winfo_exists():
            self._local_progress_label.config(text=text)

    def _show_local_error(self, msg):
        self._clear()
        f = self._panel()
        self._eyebrow(f, "Local setup")
        self._headline(f, "Let's try that again")
        self._body(f, str(msg), pady=(0, 16))
        self._primary_button(f, "Back to brain choice", self._show_brain_choice, pady=(8, 8))
        self._secondary_button(f, "Use ChatGPT instead", self._start_chatgpt_login, pady=(0, 0))

    # ─── Screen: API providers (OpenAI-compatible) ─────────────

    def _show_all_providers(self):
        import providers as _providers
        self._clear()
        f = self._panel()
        self._eyebrow(f, "Step 1 of 2")
        self._headline(f, "Connect an API provider")
        self._body(
            f,
            "Wira works with any OpenAI-compatible provider. Pick one to connect.",
            pady=(0, 12),
        )
        for p in _providers.all_presets():
            row = tk.Frame(f, bg=PANEL_ALT, padx=14, pady=10)
            row.pack(fill="x", pady=4)
            tk.Label(row, text=p["label"], font=("Avenir Next", 14, "bold"),
                     fg=TEXT, bg=PANEL_ALT, anchor="w").pack(fill="x")
            tk.Label(row, text=p["tagline"], font=FONT_SMALL, fg=TEXT_DIM,
                     bg=PANEL_ALT, anchor="w", justify="left", wraplength=420).pack(fill="x")
            self._secondary_button(row, f"Connect {p['label']}",
                                   lambda i=p["id"]: self._show_api_provider(i), pady=(8, 0))
        self._secondary_button(f, "Back", self._show_brain_choice, pady=(12, 0))

    def _show_api_provider(self, provider_id):
        import providers as _providers
        p = _providers.preset(provider_id)
        self._api_provider = provider_id
        self._clear()
        f = self._panel()
        self._eyebrow(f, "Step 1 of 2")
        self._headline(f, f"Connect {p['label']}")
        self._body(f, p["tagline"], pady=(0, 14))

        if p["needs_key"] and p["key_url"]:
            link = tk.Label(f, text=f"Get a key → {p['key_url']}", font=FONT_MONO,
                            fg=ACCENT_DARK, bg=PANEL_BG, cursor="hand2", anchor="w")
            link.pack(fill="x", pady=(0, 10))
            link.bind("<Button-1>", lambda e, u=p["key_url"]: self._open_url(u))

        self._api_key_entry = None
        self._api_base_entry = None
        if p["needs_key"]:
            tk.Label(f, text="API key", font=FONT_SMALL, fg=TEXT, bg=PANEL_BG, anchor="w").pack(fill="x")
            self._api_key_entry = tk.Entry(f, font=FONT_MONO, show="•", relief="flat", bd=6)
            self._api_key_entry.pack(fill="x", pady=(2, 10))

        if p["needs_base_url"]:
            tk.Label(f, text="Base URL", font=FONT_SMALL, fg=TEXT, bg=PANEL_BG, anchor="w").pack(fill="x")
            self._api_base_entry = tk.Entry(f, font=FONT_MONO, relief="flat", bd=6)
            self._api_base_entry.insert(0, "https://")
            self._api_base_entry.pack(fill="x", pady=(2, 10))

        tk.Label(f, text="Model (optional)", font=FONT_SMALL, fg=TEXT, bg=PANEL_BG, anchor="w").pack(fill="x")
        self._api_model_entry = tk.Entry(f, font=FONT_MONO, relief="flat", bd=6)
        self._api_model_entry.insert(0, p["default_model"])
        self._api_model_entry.pack(fill="x", pady=(2, 12))

        self._api_status = tk.Label(f, text="", font=FONT_SMALL, fg=ERROR, bg=PANEL_BG,
                                    anchor="w", justify="left", wraplength=440)
        self._api_status.pack(fill="x")

        self._api_connect_btn = self._primary_button(f, "Connect & test", self._connect_api_provider, pady=(6, 8))
        self._secondary_button(f, "Back", self._show_brain_choice, pady=(0, 0))

    def _connect_api_provider(self):
        key = self._api_key_entry.get().strip() if self._api_key_entry else None
        base = self._api_base_entry.get().strip() if self._api_base_entry else None
        model = self._api_model_entry.get().strip() or None
        self._api_status.config(fg=TEXT_SOFT, text="Testing the connection…")
        self._api_connect_btn.config(state="disabled")
        threading.Thread(
            target=self._api_test_thread,
            args=(self._api_provider, key, base, model),
            daemon=True,
        ).start()

    def _api_test_thread(self, provider_id, key, base, model):
        try:
            import providers as _providers
            ok, msg = _providers.test_provider(provider_id, api_key=key, base_url=base, model=model)
            if ok:
                _providers.save_provider(provider_id, api_key=key, model=model, base_url=base)
            self.event_queue.put(("provider_result", (ok, msg)))
        except Exception as e:
            logger.exception("Provider test error")
            self.event_queue.put(("provider_result", (False, str(e))))

    def _render_provider_result(self, data):
        ok, msg = data
        if ok:
            self._show_whatsapp()
            return
        if hasattr(self, "_api_status") and self._api_status.winfo_exists():
            self._api_status.config(fg=ERROR, text=msg)
        if hasattr(self, "_api_connect_btn") and self._api_connect_btn.winfo_exists():
            self._api_connect_btn.config(state="normal")

    # ─── Screen: ChatGPT sign-in ───────────────────────────────

    def _start_chatgpt_login(self):
        self._clear()
        f = self._panel()

        self._eyebrow(f, "Step 1 of 2")
        self._headline(f, "Connect ChatGPT")
        self._body(
            f,
            "Wira is opening a secure sign-in flow so it can use your existing ChatGPT subscription as your agent's brain.",
            pady=(0, 18),
        )
        self._bullet_row(f, "One-time connection", "You approve Wira once, then come straight back here.")
        self._bullet_row(f, "No technical setup", "You do not need to learn tools, models, or settings to finish this step.")

        self._chatgpt_status = tk.Label(f, text="Preparing your sign-in code…", font=FONT_BODY, fg=TEXT_SOFT, bg=PANEL_BG)
        self._chatgpt_status.pack(fill="x", pady=(18, 0))

        # Start login in background
        threading.Thread(target=self._chatgpt_login_thread, daemon=True).start()

    def _chatgpt_login_thread(self):
        try:
            from auth import (
                OAUTH_ISSUER, OAUTH_CLIENT_ID, OAUTH_TOKEN_URL,
                _save_auth, is_logged_in, get_access_token, device_auth_help_message,
            )
            import httpx
            import time
            from datetime import datetime, timezone

            # If already logged in, skip
            if is_logged_in():
                token = get_access_token()
                if token:
                    self.event_queue.put(("chatgpt_done", token))
                    return

            # Request device code
            with httpx.Client(timeout=15.0) as client:
                resp = client.post(
                    f"{OAUTH_ISSUER}/api/accounts/deviceauth/usercode",
                    json={"client_id": OAUTH_CLIENT_ID},
                    headers={"Content-Type": "application/json"},
                )
            if resp.status_code != 200:
                detail = f"Could not reach OpenAI (HTTP {resp.status_code})"
                if resp.status_code in {401, 403}:
                    detail = device_auth_help_message(detail)
                self.event_queue.put(("chatgpt_error", detail))
                return

            data = resp.json()
            user_code = data.get("user_code", "")
            device_auth_id = data.get("device_auth_id", "")
            poll_interval = max(3, int(data.get("interval", 5)))
            verify_url = f"{OAUTH_ISSUER}/codex/device"

            self.event_queue.put(("chatgpt_code", {"code": user_code, "url": verify_url}))

            # Poll for authorization
            start = time.monotonic()
            code_resp = None
            with httpx.Client(timeout=15.0) as client:
                while time.monotonic() - start < 900:
                    time.sleep(poll_interval)
                    poll = client.post(
                        f"{OAUTH_ISSUER}/api/accounts/deviceauth/token",
                        json={"device_auth_id": device_auth_id, "user_code": user_code},
                        headers={"Content-Type": "application/json"},
                    )
                    if poll.status_code == 200:
                        code_resp = poll.json()
                        break
                    elif poll.status_code in {403, 404}:
                        continue

            if code_resp is None:
                self.event_queue.put(("chatgpt_error", device_auth_help_message("Sign-in timed out.")))
                return

            # Exchange code for tokens
            auth_code = code_resp.get("authorization_code", "")
            code_verifier = code_resp.get("code_verifier", "")

            with httpx.Client(timeout=15.0) as client:
                token_resp = client.post(
                    OAUTH_TOKEN_URL,
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    data={
                        "grant_type": "authorization_code",
                        "code": auth_code,
                        "redirect_uri": f"{OAUTH_ISSUER}/deviceauth/callback",
                        "client_id": OAUTH_CLIENT_ID,
                        "code_verifier": code_verifier,
                    },
                )

            if token_resp.status_code != 200:
                detail = f"Token exchange failed (HTTP {token_resp.status_code})"
                if token_resp.status_code in {401, 403}:
                    detail = device_auth_help_message(detail)
                self.event_queue.put(("chatgpt_error", detail))
                return

            tokens = token_resp.json()
            result = {
                "access_token": tokens["access_token"],
                "refresh_token": tokens.get("refresh_token", ""),
                "last_refresh": datetime.now(timezone.utc).isoformat(),
                "auth_mode": "chatgpt",
            }
            _save_auth(result)
            self.event_queue.put(("chatgpt_done", tokens["access_token"]))

        except Exception as e:
            logger.exception("ChatGPT login error")
            self.event_queue.put(("chatgpt_error", str(e)))

    def _show_chatgpt_code(self, data):
        self._clear()
        f = self._panel()
        code = data["code"]
        url = data["url"]

        self._eyebrow(f, "Step 1 of 2")
        self._headline(f, "Finish connecting ChatGPT")
        self._body(f, "Open ChatGPT in your browser, enter this code, and come right back here.", pady=(0, 18))

        # Big code display
        code_frame = tk.Frame(f, bg=BG_SOFT, padx=30, pady=18)
        code_frame.pack(pady=(0, 20))
        code_label = tk.Label(code_frame, text=code, font=FONT_CODE, fg=WHITE, bg=BG_SOFT)
        code_label.pack()

        self._body(f, "Use this page:", small=True, fg=TEXT_SOFT, pady=(0, 6))

        # URL (clickable)
        url_label = tk.Label(f, text=url, font=FONT_MONO, fg=ACCENT_DARK, bg=PANEL_BG,
                             cursor="hand2")
        url_label.pack(pady=(0, 10))
        url_label.bind("<Button-1>", lambda e: self._open_url(url))

        self._body(
            f,
            "If ChatGPT says app sign-in is blocked, open ChatGPT settings, allow app sign-in, then come back here and try again.",
            small=True,
            fg=TEXT_DIM,
            pady=(0, 14),
        )

        self._primary_button(f, "Open ChatGPT", lambda: self._open_url(url), pady=(0, 12))
        self._secondary_button(f, "Try again", self._start_chatgpt_login, pady=(0, 18))

        self._waiting_label = tk.Label(f, text="Waiting for sign-in...", font=FONT_SMALL, fg=TEXT_SOFT, bg=PANEL_BG)
        self._waiting_label.pack()
        self._animate_waiting()

    def _animate_waiting(self):
        if not hasattr(self, '_waiting_label') or not self._waiting_label.winfo_exists():
            return
        dots = getattr(self, '_dot_count', 0)
        self._dot_count = (dots + 1) % 4
        self._waiting_label.config(text="Waiting for sign-in" + "." * self._dot_count)
        self.after(600, self._animate_waiting)

    def _show_chatgpt_error(self, msg):
        self._clear()
        f = self._panel()
        self._eyebrow(f, "Connection issue")
        self._headline(f, "One quick permission is needed")
        self._body(
            f,
            "Your ChatGPT account is blocking app sign-in right now. This is usually a normal account setting, not a problem with your computer.",
            pady=(0, 16),
        )
        self._body(f, str(msg), small=True, fg=TEXT_DIM, pady=(0, 18))
        self._step_row(f, 1, "Open ChatGPT settings", "Allow app sign-in for ChatGPT, then come back here.")
        self._step_row(f, 2, "Try again", "Wira will request a fresh code and keep waiting for you.")
        self._primary_button(f, "Try again", self._start_chatgpt_login, pady=(18, 8))
        self._secondary_button(f, "Open ChatGPT", lambda: self._open_url("https://chatgpt.com/"), pady=(0, 0))

    # ─── Screen: WhatsApp QR ───────────────────────────────────

    def _show_whatsapp(self):
        self._clear()
        f = self._panel()

        self._eyebrow(f, "Step 2 of 2")
        self._headline(f, "Connect WhatsApp")
        self._body(f, "Scan this code from WhatsApp to start talking to your agent.", pady=(0, 16))
        self._step_row(f, 1, "Open WhatsApp", "Go to Settings, then Linked Devices.")
        self._step_row(f, 2, "Tap Link a Device", "Point your phone at the code shown here.")

        qr_shell = tk.Frame(f, bg=PANEL_ALT, padx=18, pady=18)
        qr_shell.pack(pady=18)
        self._qr_label = tk.Label(qr_shell, text="Generating QR code...", font=FONT_SMALL, fg=TEXT_SOFT, bg=PANEL_ALT)
        self._qr_label.pack()

        self._body(f, "WhatsApp is simply the chat window. Your agent itself still lives on this computer.", small=True, fg=TEXT_DIM, center=True, pady=(4, 0))

        # Write default .env if none exists
        self._ensure_env()

        # Start WhatsApp connection in background
        threading.Thread(target=self._whatsapp_thread, daemon=True).start()

    def _ensure_env(self):
        """Write a minimal .env for first-run if setup.py hasn't been run."""
        if not ENV_FILE.exists():
            write_env([
                "LLM_PROVIDER=chatgpt",
                "OWNER_NAME=there",
                "ASSISTANT_NAME=Wira",
                "WIRA_OWNER_LOCK_ENABLED=true",
                "WIRA_EXTERNAL_MODE=ignore",
                "WIRA_PERMISSION_PRESET=balanced",
                "WIRA_REQUIRE_CONFIRMATION=true",
                "DISCLOSE_AI=true",
            ])

    def _whatsapp_thread(self):
        try:
            import importlib
            import config as _cfg
            importlib.reload(_cfg)

            from neonize.client import NewClient
            from neonize.events import ConnectedEv, QREv

            client = NewClient(_cfg.SESSION_DB_PATH)

            @client.event(QREv)
            def on_qr(c, event):
                # Sync client may pass bytes or protobuf with Codes field
                if isinstance(event, bytes):
                    qr_str = event.decode("utf-8", errors="replace")
                elif hasattr(event, "Codes") and event.Codes:
                    qr_str = list(event.Codes)[0]
                else:
                    qr_str = str(event)
                if qr_str:
                    self.event_queue.put(("qr", qr_str))

            @client.event(ConnectedEv)
            def on_connected(c, event):
                # Pairing is complete and the session is now persisted to the
                # session DB. Disconnect this pairing-only client so the agent
                # client (started in _start_agent) can own the single neonize
                # connection for this session — two live clients on one session
                # DB conflict and can trigger a WhatsApp logout.
                try:
                    client.disconnect()
                except Exception:
                    logger.warning("Could not cleanly disconnect pairing client", exc_info=True)
                self.event_queue.put(("connected", None))

            client.connect()

        except Exception as e:
            logger.exception("WhatsApp connection error")
            self.event_queue.put(("error", str(e)))

    def _render_qr(self, qr_data):
        try:
            import qrcode
            from PIL import Image, ImageTk

            qr = qrcode.QRCode(version=1, box_size=6, border=2,
                                error_correction=qrcode.constants.ERROR_CORRECT_M)
            qr.add_data(qr_data)
            qr.make(fit=True)
            img = qr.make_image(fill_color="#111111", back_color="#f7f0e4")
            img = img.resize((280, 280), Image.NEAREST)

            self._qr_photo = ImageTk.PhotoImage(img)
            self._qr_label.config(image=self._qr_photo, text="")

        except ImportError:
            # Fallback: show the data as text
            self._qr_label.config(text="QR code ready.\nOpen WhatsApp > Linked Devices\nand scan the code shown in this window.",
                                  font=FONT_SMALL, fg=TEXT_DIM)

    # ─── Screen: Live ──────────────────────────────────────────

    def _show_live(self):
        self._clear()
        f = self._panel()

        self._eyebrow(f, "Connected")
        tk.Label(f, text="✓", font=("Avenir Next", 64), fg=SUCCESS, bg=PANEL_BG).pack(pady=(8, 6))
        self._headline(f, "Your agent is ready")
        self._body(f, "Open WhatsApp and send your first message. Wira will answer there.", center=True, pady=(0, 18))
        self._step_row(f, 1, "Try: What's on my calendar today?", "A fast first proof that your agent can help with real work.")
        self._step_row(f, 2, "Try: Find the latest invoice in Downloads", "A simple way to show that your agent lives on this computer, not just in chat.")
        self._body(f, "You can close this window after this. Wira keeps your local agent available in the background.", small=True, fg=TEXT_DIM, center=True, pady=(18, 14))
        self._primary_button(f, "I'll message my agent now", self._minimize_and_run, pady=(0, 0))
        self._secondary_button(f, "Quit Wira", self.destroy, pady=(8, 0))

        # Auto-start on login
        self._install_autostart()

        # Start the agent in background
        threading.Thread(target=self._start_agent, daemon=True).start()

        # Send onboarding message
        threading.Thread(target=self._send_onboarding, daemon=True).start()

    def _show_running(self):
        """Shown when app opens and Wira is already set up."""
        self._clear()
        f = self._panel()

        self._eyebrow(f, "Wira Local")
        self._headline(f, "Your agent is already running")
        self._body(f, "Wira is connected and ready for WhatsApp messages from you.", pady=(0, 18))
        self._bullet_row(f, "Talk on WhatsApp", "That stays the simplest way to reach your agent from anywhere.")
        self._bullet_row(f, "Leave Wira installed", "Your computer is where the work happens, so keeping Wira available keeps your agent available.")

        self._primary_button(f, "Reconnect WhatsApp", self._show_whatsapp, pady=(18, 8))
        self._secondary_button(f, "Check for Updates", lambda: self._open_url(RELEASES_URL), pady=(0, 8))
        self._secondary_button(f, "Quit Wira", self.destroy, pady=(0, 0))

        # Start agent in background
        threading.Thread(target=self._start_agent, daemon=True).start()

    def _start_agent(self):
        """Run the Wira agent (brain + WhatsApp) in the background."""
        try:
            import importlib
            import config as _cfg
            importlib.reload(_cfg)

            from drafts import Drafts
            from whatsapp import WhatsApp

            drafts = Drafts()
            runtime = self._build_runtime()
            wa = WhatsApp(runtime, drafts)
            wa.run()
        except Exception as e:
            logger.exception("Agent error: %s", e)

    @staticmethod
    def _build_runtime():
        """Build the local runtime, failing closed when owner-lock is off.

        Delegates to runtime_bridge.build_local_runtime so the Hermes operator
        runtime is only used when owner-lock is enabled; otherwise (and when
        Hermes isn't installed) it falls back to the built-in responder."""
        from runtime_bridge import build_local_runtime

        return build_local_runtime()

    def _send_onboarding(self):
        """Send an onboarding message to the owner through WhatsApp."""
        import time
        time.sleep(5)  # Wait for connection to stabilize
        try:
            # The onboarding module handles the initial conversation
            from onboarding import send_welcome
            send_welcome()
        except Exception as e:
            logger.warning("Could not send onboarding message: %s", e)

    def _install_autostart(self):
        """Install a launchd plist so Wira starts on login (macOS only).

        On Windows the Inno Setup installer already offers a "Start Wira when I
        log in" shortcut under the user's Startup folder, so there's nothing to
        do here — and we must not create a bogus ~/Library/LaunchAgents folder.
        """
        if PLATFORM.system.lower() != "darwin":
            logger.info("Auto-start on login is handled by the installer on %s", PLATFORM.platform_label)
            return
        try:
            launch_agents = Path.home() / "Library" / "LaunchAgents"
            launch_agents.mkdir(parents=True, exist_ok=True)
            plist_path = launch_agents / "biz.nibiashara.wira.plist"

            # Find the app bundle path
            app_path = None
            # If running from .app bundle
            exe = Path(sys.executable)
            if ".app" in str(exe):
                app_path = str(exe).split(".app")[0] + ".app"
            elif Path("/Applications/Wira.app").exists():
                app_path = "/Applications/Wira.app"

            if not app_path:
                logger.info("Not in .app bundle — skipping auto-start install")
                return

            plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>biz.nibiashara.wira</string>
    <key>ProgramArguments</key>
    <array>
        <string>open</string>
        <string>-a</string>
        <string>{app_path}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
</dict>
</plist>
"""
            plist_path.write_text(plist_content)
            logger.info("Auto-start installed: %s", plist_path)
        except Exception as e:
            logger.warning("Could not install auto-start: %s", e)

    def _minimize_and_run(self):
        # Minimize (recoverable from the Dock/taskbar) rather than withdraw(),
        # which fully hides the window with no way to bring it back — leaving the
        # app a ghost process. The agent keeps running in the background either way.
        try:
            self.iconify()
        except Exception:
            self.withdraw()

    def _show_error(self, msg):
        # A recoverable screen, not a dead end. This is where WhatsApp pairing
        # failures land, so it must always offer a way forward (retry / go back)
        # instead of stranding the user with only force-quit.
        self._clear()
        f = self._panel()
        self._eyebrow(f, "Connection issue")
        self._headline(f, "Let's try that again")
        self._body(
            f,
            "Wira couldn't finish connecting to WhatsApp just now. This is usually "
            "a temporary hiccup — trying again normally clears it. If it keeps "
            "happening, check your internet connection.",
            pady=(0, 12),
        )
        self._body(f, str(msg), small=True, fg=TEXT_SOFT, pady=(0, 16))
        self._primary_button(f, "Try connecting again", self._show_whatsapp, pady=(6, 8))
        self._secondary_button(f, "Back to brain choice", self._show_brain_choice, pady=(0, 0))

    @staticmethod
    def _open_url(url):
        import webbrowser
        webbrowser.open(url)


def main():
    app = WiraApp()
    app.mainloop()


if __name__ == "__main__":
    main()
