#!/usr/bin/env python3
"""Wira — visual setup wizard and background agent.

No terminal. No config files. Three screens:
1. Sign in to ChatGPT
2. Scan WhatsApp QR code
3. "Wira is live — check your WhatsApp!"

After setup, Wira runs silently and onboards the user through WhatsApp itself.
"""

import logging
import os
import queue
import sys
import threading
import tkinter as tk
from io import BytesIO
from pathlib import Path

from paths import ENV_FILE, RELEASES_URL, SESSION_DB_PATH, load_env, write_env

# Load user-owned config before anything else.
load_env()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("wira.gui")

# Brand colors
BG = "#0d1a15"
BG_CARD = "#132922"
ACCENT = "#2e7d6e"
ACCENT_LIGHT = "#5ee8c5"
TEXT = "#e8ece9"
TEXT_DIM = "#8fa69b"
WHITE = "#ffffff"

FONT_TITLE = ("Helvetica Neue", 28, "bold")
FONT_HEADING = ("Helvetica Neue", 18, "bold")
FONT_BODY = ("Helvetica Neue", 14)
FONT_SMALL = ("Helvetica Neue", 12)
FONT_CODE = ("Menlo", 22, "bold")
FONT_MONO = ("Menlo", 12)

WIN_W, WIN_H = 520, 620


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
        f = self.container

        tk.Label(f, text="Wira", font=FONT_TITLE, fg=ACCENT_LIGHT, bg=BG).pack(pady=(40, 5))
        tk.Label(f, text="Your AI assistant on WhatsApp", font=FONT_BODY, fg=TEXT_DIM, bg=BG).pack(pady=(0, 40))

        tk.Label(f, text="Two quick steps:", font=FONT_HEADING, fg=TEXT, bg=BG, anchor="w").pack(fill="x", pady=(0, 15))

        steps_frame = tk.Frame(f, bg=BG)
        steps_frame.pack(fill="x", pady=(0, 30))
        for i, step in enumerate(["Sign in to ChatGPT", "Scan WhatsApp QR code"], 1):
            row = tk.Frame(steps_frame, bg=BG)
            row.pack(fill="x", pady=5)
            tk.Label(row, text=f"{i}", font=("Helvetica Neue", 14, "bold"),
                     fg=BG, bg=ACCENT_LIGHT, width=2, height=1).pack(side="left", padx=(0, 12))
            tk.Label(row, text=step, font=FONT_BODY, fg=TEXT, bg=BG, anchor="w").pack(side="left")

        tk.Label(f, text="Then Wira handles your WhatsApp.\nIt learns your voice, drafts replies, and never\nsends without your say-so.",
                 font=FONT_SMALL, fg=TEXT_DIM, bg=BG, justify="center").pack(pady=(0, 30))

        btn = tk.Button(f, text="Get Started", font=FONT_HEADING, fg=BG, bg=ACCENT_LIGHT,
                        activebackground=ACCENT, activeforeground=WHITE, relief="flat",
                        padx=40, pady=12, cursor="hand2", command=self._start_chatgpt_login)
        btn.pack()

    # ─── Screen: ChatGPT sign-in ───────────────────────────────

    def _start_chatgpt_login(self):
        self._clear()
        f = self.container

        tk.Label(f, text="Step 1 of 2", font=FONT_SMALL, fg=TEXT_DIM, bg=BG).pack(pady=(20, 5))
        tk.Label(f, text="Sign in to ChatGPT", font=FONT_HEADING, fg=TEXT, bg=BG).pack(pady=(0, 20))
        tk.Label(f, text="Connecting to OpenAI...", font=FONT_BODY, fg=TEXT_DIM, bg=BG).pack(pady=20)

        self._chatgpt_status = tk.Label(f, text="", font=FONT_SMALL, fg=TEXT_DIM, bg=BG)
        self._chatgpt_status.pack(pady=10)

        # Start login in background
        threading.Thread(target=self._chatgpt_login_thread, daemon=True).start()

    def _chatgpt_login_thread(self):
        try:
            from auth import (
                OAUTH_ISSUER, OAUTH_CLIENT_ID, OAUTH_TOKEN_URL,
                _save_auth, is_logged_in, get_access_token,
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
                self.event_queue.put(("chatgpt_error", f"Could not reach OpenAI (HTTP {resp.status_code})"))
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
                self.event_queue.put(("chatgpt_error", "Sign-in timed out. Please restart and try again."))
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
                self.event_queue.put(("chatgpt_error", "Token exchange failed. Please try again."))
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
        f = self.container
        code = data["code"]
        url = data["url"]

        tk.Label(f, text="Step 1 of 2", font=FONT_SMALL, fg=TEXT_DIM, bg=BG).pack(pady=(20, 5))
        tk.Label(f, text="Sign in to ChatGPT", font=FONT_HEADING, fg=TEXT, bg=BG).pack(pady=(0, 25))

        tk.Label(f, text="Enter this code:", font=FONT_BODY, fg=TEXT_DIM, bg=BG).pack(pady=(0, 10))

        # Big code display
        code_frame = tk.Frame(f, bg=BG_CARD, padx=30, pady=15)
        code_frame.pack(pady=(0, 20))
        code_label = tk.Label(code_frame, text=code, font=FONT_CODE, fg=ACCENT_LIGHT, bg=BG_CARD)
        code_label.pack()

        tk.Label(f, text="at", font=FONT_BODY, fg=TEXT_DIM, bg=BG).pack(pady=(0, 5))

        # URL (clickable)
        url_label = tk.Label(f, text=url, font=FONT_MONO, fg=ACCENT_LIGHT, bg=BG,
                             cursor="hand2")
        url_label.pack(pady=(0, 15))
        url_label.bind("<Button-1>", lambda e: self._open_url(url))

        btn = tk.Button(f, text="Open Browser", font=FONT_BODY, fg=BG, bg=ACCENT_LIGHT,
                        activebackground=ACCENT, activeforeground=WHITE, relief="flat",
                        padx=20, pady=8, cursor="hand2", command=lambda: self._open_url(url))
        btn.pack(pady=(0, 25))

        self._waiting_label = tk.Label(f, text="Waiting for sign-in...", font=FONT_SMALL, fg=TEXT_DIM, bg=BG)
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
        f = self.container
        tk.Label(f, text="Something went wrong", font=FONT_HEADING, fg="#e74c3c", bg=BG).pack(pady=(60, 20))
        tk.Label(f, text=msg, font=FONT_BODY, fg=TEXT_DIM, bg=BG, wraplength=400).pack(pady=(0, 30))
        tk.Button(f, text="Try Again", font=FONT_BODY, fg=BG, bg=ACCENT_LIGHT,
                  relief="flat", padx=20, pady=8, cursor="hand2",
                  command=self._start_chatgpt_login).pack()

    # ─── Screen: WhatsApp QR ───────────────────────────────────

    def _show_whatsapp(self):
        self._clear()
        f = self.container

        tk.Label(f, text="Step 2 of 2", font=FONT_SMALL, fg=TEXT_DIM, bg=BG).pack(pady=(20, 5))
        tk.Label(f, text="Connect WhatsApp", font=FONT_HEADING, fg=TEXT, bg=BG).pack(pady=(0, 15))
        tk.Label(f, text="Scan this QR code with WhatsApp", font=FONT_BODY, fg=TEXT_DIM, bg=BG).pack(pady=(0, 5))
        tk.Label(f, text="Settings > Linked Devices > Link a Device", font=FONT_SMALL, fg=TEXT_DIM, bg=BG).pack(pady=(0, 15))

        self._qr_label = tk.Label(f, text="Generating QR code...", font=FONT_SMALL, fg=TEXT_DIM, bg=BG)
        self._qr_label.pack(pady=20)

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
                "APPROVAL_MODE=draft",
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
            img = qr.make_image(fill_color="#ffffff", back_color=BG_CARD)
            img = img.resize((280, 280), Image.NEAREST)

            self._qr_photo = ImageTk.PhotoImage(img)
            self._qr_label.config(image=self._qr_photo, text="")

        except ImportError:
            # Fallback: show the data as text
            self._qr_label.config(text="QR code ready.\nOpen WhatsApp > Linked Devices\nand scan the code in the terminal.",
                                  font=FONT_SMALL, fg=TEXT_DIM)

    # ─── Screen: Live ──────────────────────────────────────────

    def _show_live(self):
        self._clear()
        f = self.container

        tk.Label(f, text="✓", font=("Helvetica Neue", 64), fg=ACCENT_LIGHT, bg=BG).pack(pady=(50, 10))
        tk.Label(f, text="Wira is live!", font=FONT_TITLE, fg=TEXT, bg=BG).pack(pady=(0, 15))
        tk.Label(f, text="Check your WhatsApp — Wira will\nmessage you to finish setting up.",
                 font=FONT_BODY, fg=TEXT_DIM, bg=BG, justify="center").pack(pady=(0, 30))
        tk.Label(f, text="You can close this window.\nWira keeps running in the background.",
                 font=FONT_SMALL, fg=TEXT_DIM, bg=BG, justify="center").pack(pady=(0, 30))

        tk.Button(f, text="Close", font=FONT_BODY, fg=TEXT_DIM, bg=BG_CARD,
                  activebackground=ACCENT, activeforeground=WHITE, relief="flat",
                  padx=20, pady=8, cursor="hand2",
                  command=self._minimize_and_run).pack()

        # Auto-start on login
        self._install_autostart()

        # Start the agent in background
        threading.Thread(target=self._start_agent, daemon=True).start()

        # Send onboarding message
        threading.Thread(target=self._send_onboarding, daemon=True).start()

    def _show_running(self):
        """Shown when app opens and Wira is already set up."""
        self._clear()
        f = self.container

        tk.Label(f, text="Wira", font=FONT_TITLE, fg=ACCENT_LIGHT, bg=BG).pack(pady=(50, 10))
        tk.Label(f, text="Running", font=FONT_HEADING, fg=ACCENT_LIGHT, bg=BG).pack(pady=(0, 20))
        tk.Label(f, text="Wira is connected to your WhatsApp\nand handling messages.",
                 font=FONT_BODY, fg=TEXT_DIM, bg=BG, justify="center").pack(pady=(0, 30))

        tk.Button(f, text="Reconnect WhatsApp", font=FONT_BODY, fg=BG, bg=ACCENT_LIGHT,
                  activebackground=ACCENT, activeforeground=WHITE, relief="flat",
                  padx=20, pady=8, cursor="hand2",
                  command=self._show_whatsapp).pack(pady=(0, 10))

        tk.Button(f, text="Check for Updates", font=FONT_BODY, fg=TEXT, bg=BG_CARD,
                  activebackground=ACCENT, activeforeground=WHITE, relief="flat",
                  padx=20, pady=8, cursor="hand2",
                  command=lambda: self._open_url(RELEASES_URL)).pack(pady=(0, 10))

        tk.Button(f, text="Quit Wira", font=FONT_SMALL, fg=TEXT_DIM, bg=BG_CARD,
                  activebackground="#3a1515", activeforeground="#e74c3c", relief="flat",
                  padx=15, pady=6, cursor="hand2",
                  command=self.destroy).pack(pady=(10, 0))

        # Start agent in background
        threading.Thread(target=self._start_agent, daemon=True).start()

    def _start_agent(self):
        """Run the Wira agent (brain + WhatsApp) in the background."""
        try:
            import importlib
            import config as _cfg
            importlib.reload(_cfg)

            from brain import Brain
            from drafts import Drafts
            from memory import Memory
            from whatsapp import WhatsApp

            memory = Memory()
            drafts = Drafts()
            brain = Brain(memory)
            wa = WhatsApp(brain, drafts)
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
