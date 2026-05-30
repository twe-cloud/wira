"""Wira auth — OAuth device code flow for ChatGPT subscriptions.

Users log in with their existing ChatGPT account. No API key needed.
Tokens are stored locally in ~/.wira/auth.json and refreshed automatically.
"""

import base64
import json
import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

logger = logging.getLogger("wira.auth")

OAUTH_ISSUER = "https://auth.openai.com"
OAUTH_CLIENT_ID = "app_EMoamEEZ73f0CkXaXp7hrann"
OAUTH_TOKEN_URL = f"{OAUTH_ISSUER}/oauth/token"
CODEX_BASE_URL = "https://chatgpt.com/backend-api/codex"

AUTH_DIR = Path.home() / ".wira"
AUTH_FILE = AUTH_DIR / "auth.json"


def _load_auth() -> dict:
    if AUTH_FILE.exists():
        try:
            return json.loads(AUTH_FILE.read_text())
        except Exception:
            pass
    return {}


def _save_auth(data: dict) -> None:
    AUTH_DIR.mkdir(parents=True, exist_ok=True)
    AUTH_FILE.write_text(json.dumps(data, indent=2))
    # Restrict permissions — tokens are sensitive
    AUTH_FILE.chmod(0o600)


def get_access_token() -> str | None:
    """Return a valid access token, refreshing if needed."""
    auth = _load_auth()
    access = auth.get("access_token", "")
    refresh = auth.get("refresh_token", "")
    if not access and not refresh:
        return None
    # Try refreshing proactively — access tokens are short-lived
    if refresh:
        try:
            new_tokens = refresh_tokens(refresh)
            _save_auth({**auth, **new_tokens})
            return new_tokens["access_token"]
        except Exception as e:
            logger.warning("Token refresh failed: %s — using existing token", e)
    return access or None


def refresh_tokens(refresh_token: str) -> dict:
    """Exchange a refresh token for fresh access + refresh tokens."""
    with httpx.Client(timeout=20.0) as client:
        resp = client.post(
            OAUTH_TOKEN_URL,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": OAUTH_CLIENT_ID,
            },
        )
    if resp.status_code != 200:
        raise RuntimeError(f"Token refresh failed (HTTP {resp.status_code})")
    tokens = resp.json()
    return {
        "access_token": tokens["access_token"],
        "refresh_token": tokens.get("refresh_token", refresh_token),
        "last_refresh": datetime.now(timezone.utc).isoformat(),
    }


def cloudflare_headers(access_token: str) -> dict:
    """Headers to pass Cloudflare on chatgpt.com/backend-api/codex."""
    headers = {
        "User-Agent": "codex_cli_rs/0.0.0 (Wira Agent)",
        "originator": "codex_cli_rs",
    }
    try:
        parts = access_token.split(".")
        if len(parts) >= 2:
            payload = parts[1] + "=" * (-len(parts[1]) % 4)
            claims = json.loads(base64.urlsafe_b64decode(payload))
            acct_id = claims.get("https://api.openai.com/auth", {}).get("chatgpt_account_id")
            if acct_id:
                headers["ChatGPT-Account-ID"] = acct_id
    except Exception:
        pass
    return headers


def device_code_login() -> dict:
    """Run the OpenAI device code login flow. Returns tokens dict.

    Prints a code for the user to enter at auth.openai.com/codex/device.
    Blocks until the user completes login (up to 15 minutes).
    """
    # Step 1: Request device code
    with httpx.Client(timeout=15.0) as client:
        resp = client.post(
            f"{OAUTH_ISSUER}/api/accounts/deviceauth/usercode",
            json={"client_id": OAUTH_CLIENT_ID},
            headers={"Content-Type": "application/json"},
        )
    if resp.status_code != 200:
        raise RuntimeError(f"Device code request failed (HTTP {resp.status_code})")

    data = resp.json()
    user_code = data.get("user_code", "")
    device_auth_id = data.get("device_auth_id", "")
    poll_interval = max(3, int(data.get("interval", 5)))

    if not user_code or not device_auth_id:
        raise RuntimeError("Device code response incomplete")

    # Step 2: Show the code
    print()
    print("  Sign in with your ChatGPT account:")
    print()
    print(f"  1. Open:  \033[94m{OAUTH_ISSUER}/codex/device\033[0m")
    print(f"  2. Enter: \033[1m{user_code}\033[0m")
    print()
    print("  Waiting for you to sign in... (Ctrl+C to cancel)")

    # Step 3: Poll for authorization
    start = time.monotonic()
    code_resp = None

    try:
        with httpx.Client(timeout=15.0) as client:
            while time.monotonic() - start < 900:  # 15 min
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
                else:
                    raise RuntimeError(f"Polling failed (HTTP {poll.status_code})")
    except KeyboardInterrupt:
        print("\n  Cancelled.")
        raise SystemExit(1)

    if code_resp is None:
        raise RuntimeError("Login timed out")

    # Step 4: Exchange code for tokens
    auth_code = code_resp.get("authorization_code", "")
    code_verifier = code_resp.get("code_verifier", "")
    if not auth_code or not code_verifier:
        raise RuntimeError("Auth response missing authorization_code or code_verifier")

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
        raise RuntimeError(f"Token exchange failed (HTTP {token_resp.status_code})")

    tokens = token_resp.json()
    result = {
        "access_token": tokens["access_token"],
        "refresh_token": tokens.get("refresh_token", ""),
        "last_refresh": datetime.now(timezone.utc).isoformat(),
        "auth_mode": "chatgpt",
    }

    _save_auth(result)
    return result


def is_logged_in() -> bool:
    """Check if we have stored tokens."""
    auth = _load_auth()
    return bool(auth.get("access_token") or auth.get("refresh_token"))


def logout() -> None:
    """Clear stored tokens."""
    if AUTH_FILE.exists():
        AUTH_FILE.unlink()
        print("  Logged out. Tokens cleared.")
