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

# Hard ceilings so a stuck Hermes call can't hang the WhatsApp handler forever.
HERMES_REPLY_TIMEOUT_SECONDS = 300
HERMES_PROFILE_TIMEOUT_SECONDS = 60


class HermesRuntime:
    # Marks this as the owner's operator runtime — it can run terminal/file
    # tools on the machine. Used to keep non-owner messages away from it and to
    # refuse it when owner-lock is off. See build_local_runtime().
    is_operator_runtime = True

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
            timeout=HERMES_PROFILE_TIMEOUT_SECONDS,
        )
        if show.returncode != 0:
            create = subprocess.run(
                [self.hermes_command, "profile", "create", self.profile, "--clone", "--no-alias"],
                capture_output=True,
                text=True,
                env=self._env(),
                timeout=HERMES_PROFILE_TIMEOUT_SECONDS,
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
        cmd = [self.hermes_command, "--profile", self.profile]
        # Only auto-approve every tool call when the owner explicitly chose the
        # "move fast" mode. With confirmation required (the default, and the
        # option onboarding recommends), we must NOT pass --yolo — otherwise the
        # safety choice is cosmetic and destructive/injected actions run
        # unattended. Without --yolo the agent stops to ask before risky steps.
        if not config.WIRA_REQUIRE_CONFIRMATION:
            cmd.append("--yolo")
        cmd.extend(["-z", self._build_prompt(sender_name, text)])
        if self.toolsets:
            cmd.extend(["-t", ",".join(self.toolsets)])

        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.workdir,
                env=self._env(),
                timeout=HERMES_REPLY_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired:
            return (
                f"{config.ASSISTANT_NAME} timed out working on that. Try a smaller "
                "step, or confirm explicitly before re-running anything risky."
            )
        if proc.returncode != 0:
            detail = (proc.stderr or proc.stdout).strip()
            raise RuntimeError(detail or "Hermes runtime command failed")
        return (proc.stdout or "").strip() or f"{config.ASSISTANT_NAME} ran, but returned no text."


def build_local_runtime():
    """Build the runtime for the local WhatsApp agent, failing closed.

    The Hermes operator runtime can run terminal/file commands, so it is only
    safe when owner-lock is on (only the linked owner can issue commands). If
    owner-lock is disabled we refuse the operator runtime and fall back to the
    plain LLM responder — we never hand every sender shell access. When Hermes
    isn't installed we also fall back, so a fresh machine still answers.
    """
    import logging

    from brain import Brain
    from memory import Memory

    log = logging.getLogger("wira.runtime_bridge")

    if not config.WIRA_OWNER_LOCK_ENABLED:
        log.warning(
            "Owner lock is OFF — refusing the Hermes operator runtime and using "
            "the built-in %s responder so non-owner messages can't run commands.",
            config.LLM_PROVIDER,
        )
        return Brain(Memory())

    try:
        return HermesRuntime()
    except RuntimeError as e:
        log.warning(
            "Hermes CLI unavailable (%s). Falling back to the built-in %s responder.",
            e,
            config.LLM_PROVIDER,
        )
        return Brain(Memory())
