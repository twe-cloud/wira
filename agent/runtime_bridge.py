"""Bridge local Wira commands into a real Hermes runtime/profile."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import config
from paths import WIRA_DIR

RUNTIME_METADATA_PATH = WIRA_DIR / "runtime.json"


class HermesRuntime:
    def __init__(
        self,
        hermes_command: str | None = None,
        profile: str | None = None,
        workdir: str | None = None,
        toolsets: list[str] | None = None,
    ):
        self.hermes_command = hermes_command or config.WIRA_HERMES_COMMAND or self._discover_hermes_command()
        self.profile = profile or config.WIRA_HERMES_PROFILE
        self.workdir = workdir or config.WIRA_HERMES_WORKDIR
        self.toolsets = toolsets or list(config.WIRA_ALLOWED_TOOLSETS)
        self._profile_ready = False
        self._write_metadata()

    def _discover_hermes_command(self) -> str:
        # PATH first (shutil.which honors PATHEXT on Windows, so it finds
        # hermes.exe / hermes.cmd too), then the standard per-user install dir.
        home = Path.home()
        candidates = [
            shutil.which("hermes"),
            str(home / ".hermes" / "node" / "bin" / "hermes"),
            str(home / ".hermes" / "bin" / "hermes"),
        ]
        for candidate in candidates:
            if candidate and Path(candidate).exists():
                return candidate
        raise RuntimeError(
            "Hermes CLI not found. Set WIRA_HERMES_COMMAND or install Hermes before starting Wira."
        )

    def _write_metadata(self) -> None:
        WIRA_DIR.mkdir(parents=True, exist_ok=True)
        RUNTIME_METADATA_PATH.write_text(
            json.dumps(
                {
                    "profile": self.profile,
                    "hermes_command": self.hermes_command,
                    "workdir": self.workdir,
                    "toolsets": self.toolsets,
                },
                indent=2,
            )
        )

    def ensure_profile(self) -> None:
        if self._profile_ready:
            return

        show = subprocess.run(
            [self.hermes_command, "profile", "show", self.profile],
            capture_output=True,
            text=True,
            env=self._env(),
        )
        if show.returncode != 0:
            create = subprocess.run(
                [self.hermes_command, "profile", "create", self.profile, "--clone", "--no-alias"],
                capture_output=True,
                text=True,
                env=self._env(),
            )
            if create.returncode != 0:
                raise RuntimeError(create.stderr.strip() or create.stdout.strip() or "Failed to create Hermes profile")
        self._profile_ready = True

    def _env(self) -> dict[str, str]:
        env = os.environ.copy()
        env.setdefault("HERMES_ACCEPT_HOOKS", "1")
        return env

    def _build_prompt(self, sender_name: str, text: str) -> str:
        confirmation_rule = (
            "If a command would be destructive, high-risk, or ambiguous, stop and ask for confirmation before acting."
            if config.WIRA_REQUIRE_CONFIRMATION
            else "Move fast on normal commands. Only stop when something is destructive, unclear, or permission-blocked."
        )
        return (
            f"You are {config.ASSISTANT_NAME}, the Wira-branded Hermes agent for {config.OWNER_NAME}. "
            f"You are replying inside a private WhatsApp chat with the owner. "
            f"Do the work using Hermes tools when needed, then reply in a concise phone-friendly style. "
            f"Use the current working directory as your local machine starting point unless the task clearly points elsewhere. "
            f"{confirmation_rule}\n\n"
            f"Owner display name: {sender_name}\n"
            f"Owner command: {text}"
        )

    def reply(self, chat: str, sender_name: str, text: str) -> str:
        self.ensure_profile()
        cmd = [
            self.hermes_command,
            "--profile",
            self.profile,
            "--yolo",
            "-z",
            self._build_prompt(sender_name, text),
        ]
        if self.toolsets:
            cmd.extend(["-t", ",".join(self.toolsets)])

        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=self.workdir,
            env=self._env(),
        )
        if proc.returncode != 0:
            detail = (proc.stderr or proc.stdout).strip()
            raise RuntimeError(detail or "Hermes runtime command failed")
        return (proc.stdout or "").strip() or f"{config.ASSISTANT_NAME} ran, but returned no text."
