"""Wira configuration — all knobs read from environment (.env)."""

import os
from pathlib import Path

from paths import SESSION_DB_PATH as DEFAULT_SESSION_DB_PATH

AGENT_DIR = Path(__file__).parent

# --- Identity ---
OWNER_NAME = os.getenv("OWNER_NAME", "Craig")
ASSISTANT_NAME = os.getenv("ASSISTANT_NAME", "Wira")
BUSINESS_NAME = (
    os.getenv("BUSINESS_NAME")
    or os.getenv("CLIENT_BUSINESS_NAME")
    or OWNER_NAME
).strip()
CUSTOMER_VISIBLE_ASSISTANT_NAME = os.getenv("CUSTOMER_VISIBLE_ASSISTANT_NAME", "").strip()
WIRA_PROMPT_PROFILE = os.getenv("WIRA_PROMPT_PROFILE", "local").strip().lower()

# --- Brain (LLM provider) ---
# "chatgpt"   = easy ChatGPT subscription path (kept as the env fallback if no
#                onboarding choices have been saved yet)
# "anthropic" = Claude API (needs ANTHROPIC_API_KEY)
# "openai"    = GPT API (needs OPENAI_API_KEY)
# "ollama"    = local model (private, free, needs Ollama running)
# Plus any OpenAI-compatible provider below (just a base_url + key swap):
# "openrouter", "groq", "deepseek", "xai", "together", "fireworks",
# "mistral", "gemini", "lmstudio" (local), "openai-compatible" (custom URL).
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "chatgpt").lower()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
# Base URL for the generic "openai-compatible" provider (any OpenAI-shaped API).
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "")

# OpenAI-compatible providers — all reuse the OpenAI SDK with a different
# base_url, so adding one is a config entry, not new client code. key_env=None
# means no API key is required (local servers like LM Studio). base_url=None
# means the URL is taken from OPENAI_BASE_URL at runtime (the custom path).
OPENAI_COMPATIBLE_PROVIDERS = {
    "openrouter": {
        "label": "OpenRouter",
        "base_url": "https://openrouter.ai/api/v1",
        "key_env": "OPENROUTER_API_KEY",
        "default_model": "openai/gpt-4o-mini",
    },
    "groq": {
        "label": "Groq",
        "base_url": "https://api.groq.com/openai/v1",
        "key_env": "GROQ_API_KEY",
        "default_model": "llama-3.3-70b-versatile",
    },
    "deepseek": {
        "label": "DeepSeek",
        "base_url": "https://api.deepseek.com",
        "key_env": "DEEPSEEK_API_KEY",
        "default_model": "deepseek-chat",
    },
    "xai": {
        "label": "xAI Grok",
        "base_url": "https://api.x.ai/v1",
        "key_env": "XAI_API_KEY",
        "default_model": "grok-2-latest",
    },
    "together": {
        "label": "Together AI",
        "base_url": "https://api.together.xyz/v1",
        "key_env": "TOGETHER_API_KEY",
        "default_model": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
    },
    "fireworks": {
        "label": "Fireworks AI",
        "base_url": "https://api.fireworks.ai/inference/v1",
        "key_env": "FIREWORKS_API_KEY",
        "default_model": "accounts/fireworks/models/llama-v3p3-70b-instruct",
    },
    "mistral": {
        "label": "Mistral",
        "base_url": "https://api.mistral.ai/v1",
        "key_env": "MISTRAL_API_KEY",
        "default_model": "mistral-small-latest",
    },
    "gemini": {
        "label": "Google Gemini",
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "key_env": "GEMINI_API_KEY",
        "default_model": "gemini-2.0-flash",
    },
    "lmstudio": {
        "label": "LM Studio (local)",
        "base_url": "http://localhost:1234/v1",
        "key_env": None,
        "default_model": "local-model",
    },
    "openai-compatible": {
        "label": "Custom (OpenAI-compatible)",
        "base_url": None,  # read from OPENAI_BASE_URL
        "key_env": "OPENAI_API_KEY",
        "default_model": "gpt-4o-mini",
    },
}

# Default model per provider (overridable with LLM_MODEL)
_DEFAULT_MODEL = {
    "chatgpt": "gpt-4o",
    "anthropic": "claude-sonnet-4-6",
    "openai": "gpt-4o-mini",
    "ollama": "llama3.2:3b",
}


def _default_model_for(provider: str) -> str:
    if provider in _DEFAULT_MODEL:
        return _DEFAULT_MODEL[provider]
    cfg = OPENAI_COMPATIBLE_PROVIDERS.get(provider)
    if cfg:
        return cfg["default_model"]
    return "gpt-4o"


LLM_MODEL = os.getenv("LLM_MODEL") or _default_model_for(LLM_PROVIDER)

MAX_TOKENS = int(os.getenv("MAX_TOKENS", "400"))

# --- Behaviour ---
# Reply inside group chats too? Default: DMs only (groups get noisy fast).
REPLY_TO_GROUPS = os.getenv("REPLY_TO_GROUPS", "false").lower() in ("1", "true", "yes")

# Optional allowlist of phone numbers (digits only, no +). Empty = reply to everyone.
_raw_allow = os.getenv("ALLOWLIST", "").strip()
ALLOWLIST = {n.strip().lstrip("+") for n in _raw_allow.split(",") if n.strip()}

# --- Wira local runtime policy ---
WIRA_OWNER_LOCK_ENABLED = os.getenv("WIRA_OWNER_LOCK_ENABLED", "true").lower() in ("1", "true", "yes")
WIRA_EXTERNAL_MODE = os.getenv("WIRA_EXTERNAL_MODE", "ignore").strip().lower()
WIRA_PERMISSION_PRESET = os.getenv("WIRA_PERMISSION_PRESET", "balanced").strip().lower()
WIRA_REQUIRE_CONFIRMATION = os.getenv("WIRA_REQUIRE_CONFIRMATION", "true").lower() in ("1", "true", "yes")
WIRA_HERMES_PROFILE = os.getenv("WIRA_HERMES_PROFILE", "wira-local").strip() or "wira-local"
WIRA_HERMES_COMMAND = os.getenv("WIRA_HERMES_COMMAND", "").strip()
WIRA_HERMES_WORKDIR = os.getenv("WIRA_HERMES_WORKDIR", str(Path.home())).strip() or str(Path.home())

_PERMISSION_TOOLSETS = {
    "desk": ["session_search", "skills"],
    "balanced": ["file", "web", "session_search", "skills"],
    "operator": ["file", "terminal", "web", "session_search", "skills", "vision"],
}
WIRA_ALLOWED_TOOLSETS = _PERMISSION_TOOLSETS.get(WIRA_PERMISSION_PRESET, _PERMISSION_TOOLSETS["balanced"])

# --- Approval mode ---
# Legacy responder-mode controls. Local owner-command mode ignores these unless
# WIRA_EXTERNAL_MODE is switched away from "ignore" for an optional later workflow.
# "auto-all"     : Wira sends every reply it generates (fastest, riskiest)
# "auto-trusted" : Wira auto-sends to contacts in AUTO_SEND_TO; drafts for everyone else
# "draft"        : Wira drafts but never auto-sends — operator/customer reviews drafts
APPROVAL_MODE = os.getenv("APPROVAL_MODE", "auto-trusted").lower()
_raw_trusted = os.getenv("AUTO_SEND_TO", "").strip()
AUTO_SEND_TO = {n.strip().lstrip("+") for n in _raw_trusted.split(",") if n.strip()}

# Where drafts are recorded when not auto-sent
DRAFTS_DB_PATH = os.getenv("DRAFTS_DB_PATH", str(Path.home() / ".wira" / "drafts.db"))

# Voice samples — a few recent messages the owner has sent.
# Joined with newlines and dropped into the system prompt as examples.
# Either inline as a single env var (newline-separated) or pointed at a file.
_voice_inline = os.getenv("VOICE_SAMPLES", "").strip()
_voice_file = os.getenv("VOICE_SAMPLES_FILE", "").strip()
if _voice_inline:
    VOICE_SAMPLES = _voice_inline
elif _voice_file and Path(_voice_file).exists():
    VOICE_SAMPLES = Path(_voice_file).read_text().strip()
else:
    VOICE_SAMPLES = ""

# Whether Wira openly identifies as an AI assistant when asked.
DISCLOSE_AI = os.getenv("DISCLOSE_AI", "true").lower() in ("1", "true", "yes")

# --- Storage ---
# WhatsApp session (device pairing). Delete this file to re-pair / log out.
SESSION_DB_PATH = os.getenv("SESSION_DB_PATH", str(DEFAULT_SESSION_DB_PATH))
# Conversation memory.
MEMORY_DB_PATH = os.getenv("MEMORY_DB_PATH", str(Path.home() / ".wira" / "memory.db"))

MAX_HISTORY_MESSAGES = int(os.getenv("MAX_HISTORY_MESSAGES", "20"))  # per-contact context
MAX_STORED_MESSAGES = int(os.getenv("MAX_STORED_MESSAGES", "5000"))  # global prune ceiling

# --- WhatsApp Business Cloud API ---
# Official WhatsApp Business transport. This is separate from the QR-linked
# personal-number transport in whatsapp.py.
#
# Wira accepts both its own WHATSAPP_CLOUD_* names and the shared Ni Biashara
# Meta profile names used by credential_guard.py (`meta-whatsapp-ni-biashara-cloud-api`).
# Keep this alias layer server-side only; never ship these values in the desktop app.
WHATSAPP_CLOUD_ACCESS_TOKEN = os.getenv("WHATSAPP_CLOUD_ACCESS_TOKEN") or os.getenv("WHATSAPP_ACCESS_TOKEN", "")
WHATSAPP_CLOUD_PHONE_NUMBER_ID = os.getenv("WHATSAPP_CLOUD_PHONE_NUMBER_ID") or os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
WHATSAPP_CLOUD_VERIFY_TOKEN = os.getenv("WHATSAPP_CLOUD_VERIFY_TOKEN") or os.getenv("WHATSAPP_WEBHOOK_VERIFY_TOKEN", "")
WHATSAPP_CLOUD_APP_SECRET = os.getenv("WHATSAPP_CLOUD_APP_SECRET") or os.getenv("WHATSAPP_APP_SECRET", "")
WHATSAPP_CLOUD_REQUIRE_SIGNATURE = os.getenv(
    "WHATSAPP_CLOUD_REQUIRE_SIGNATURE",
    "true",
).lower() in ("1", "true", "yes")
WHATSAPP_CLOUD_GRAPH_VERSION = os.getenv("WHATSAPP_CLOUD_GRAPH_VERSION", "v23.0")
WHATSAPP_CLOUD_WEBHOOK_PATH = os.getenv("WHATSAPP_CLOUD_WEBHOOK_PATH", "/webhooks/whatsapp")
# Loopback by default: the webhook serves plain HTTP and must sit behind a TLS
# proxy. Set WHATSAPP_CLOUD_HOST=0.0.0.0 only in a managed deployment where a
# proxy terminates TLS and forwards to it.
WHATSAPP_CLOUD_HOST = os.getenv("WHATSAPP_CLOUD_HOST", "127.0.0.1")
WHATSAPP_CLOUD_PORT = int(os.getenv("WHATSAPP_CLOUD_PORT", "8080"))
WHATSAPP_CLOUD_DB_PATH = os.getenv(
    "WHATSAPP_CLOUD_DB_PATH",
    str(Path.home() / ".wira" / "whatsapp_cloud.db"),
)
