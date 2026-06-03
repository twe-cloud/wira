#!/usr/bin/env python3
"""Wira — visual setup wizard and background agent.

The product promise is simple:
1. Wira runs on this computer.
2. It connects to the user's existing ChatGPT account.
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

# Load user-owned config before anything else.
load_env()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("wira.gui")

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
                if event_type == "chatgpt_code":
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

        self._eyebrow(f, "Wira Local")
        self._headline(f, "Talk to your agent on WhatsApp")
        self._body(
            f,
            "Wira sets up a personal agent on this computer, connects it to your ChatGPT subscription, and brings it to WhatsApp as fast as possible.",
            pady=(0, 18),
        )

        self._bullet_row(f, "Runs on this computer", "That is what lets your agent do real work for you instead of acting like a toy chat window.")
        self._bullet_row(f, "Uses the ChatGPT account you already pay for", "You connect once, then Wira keeps using that subscription as your agent's brain.")
        self._bullet_row(f, "Starts on WhatsApp", "Your phone becomes the easiest way to talk to your agent while the actual work happens here.")

        self._body(f, "Setup takes two steps.", fg=TEXT, small=True, pady=(20, 8))
        self._step_row(f, 1, "Connect ChatGPT", "Approve Wira to use your existing ChatGPT subscription.")
        self._step_row(f, 2, "Connect WhatsApp", "Scan one code so you can start texting your agent immediately.")

        self._primary_button(f, "Set up my agent", self._start_chatgpt_login, pady=(22, 0))

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
                "ASSISTANT_NAME=Vera",
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
                self.event_queue.put(("connected", None))
                # Store the client for the agent to use
                self._wa_client = client

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
        self._body(f, "Open WhatsApp and send your first message. Vera will answer there.", center=True, pady=(0, 18))
        self._step_row(f, 1, "Try: What's on my calendar today?", "A fast first proof that your agent can help with real work.")
        self._step_row(f, 2, "Try: Find the latest invoice in Downloads", "A simple way to show that your agent lives on this computer, not just in chat.")
        self._body(f, "You can close this window after this. Wira keeps your local agent available in the background.", small=True, fg=TEXT_DIM, center=True, pady=(18, 14))
        self._primary_button(f, "I'll message my agent now", self._minimize_and_run, pady=(0, 0))

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
            from runtime_bridge import HermesRuntime
            from whatsapp import WhatsApp

            runtime = HermesRuntime()
            drafts = Drafts()
            wa = WhatsApp(runtime, drafts)
            wa.run()
        except Exception as e:
            logger.exception("Agent error: %s", e)

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
        """Install a launchd plist so Wira starts on login."""
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
        self.withdraw()

    def _show_error(self, msg):
        self._clear()
        f = self.container
        tk.Label(f, text="Something went wrong", font=FONT_HEADING, fg="#e74c3c", bg=BG).pack(pady=(60, 20))
        tk.Label(f, text=str(msg), font=FONT_BODY, fg=TEXT_DIM, bg=BG, wraplength=400).pack(pady=(0, 30))

    @staticmethod
    def _open_url(url):
        import webbrowser
        webbrowser.open(url)


def main():
    app = WiraApp()
    app.mainloop()


if __name__ == "__main__":
    main()
