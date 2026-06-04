"""Shared Wira local paths and small config helpers."""

import os
import shutil
from pathlib import Path

AGENT_DIR = Path(__file__).parent
WIRA_DIR = Path.home() / ".wira"
ENV_FILE = WIRA_DIR / ".env"
SESSION_DB_PATH = WIRA_DIR / "session.sqlite3"
RELEASES_URL = "https://github.com/twe-cloud/wira/releases/latest"


def ensure_wira_dir() -> None:
    WIRA_DIR.mkdir(parents=True, exist_ok=True)
    # The dir holds .env (secrets) and the session DB — lock it down.
    try:
        WIRA_DIR.chmod(0o700)
    except OSError:
        pass


def migrate_legacy_state() -> None:
    """Move old app-bundle-local state into the user's Wira folder."""
    ensure_wira_dir()
    for name, target in ((".env", ENV_FILE), ("session.sqlite3", SESSION_DB_PATH)):
        legacy = AGENT_DIR / name
        if legacy.exists() and not target.exists():
            try:
                shutil.copy2(legacy, target)
                target.chmod(0o600)
            except Exception:
                pass


def load_env() -> None:
    migrate_legacy_state()
    if not ENV_FILE.exists():
        return
    for line in ENV_FILE.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())


def write_env(lines: list[str]) -> None:
    ensure_wira_dir()
    ENV_FILE.write_text("\n".join(lines) + "\n")
    ENV_FILE.chmod(0o600)


def update_env(key: str, value: str) -> None:
    ensure_wira_dir()
    if not ENV_FILE.exists():
        write_env([f"{key}={value}"])
        return

    lines = ENV_FILE.read_text().splitlines()
    found = False
    new_lines = []
    for line in lines:
        if line.strip().startswith(f"{key}="):
            new_lines.append(f"{key}={value}")
            found = True
        else:
            new_lines.append(line)
    if not found:
        new_lines.append(f"{key}={value}")
    write_env(new_lines)
    os.environ[key] = value
