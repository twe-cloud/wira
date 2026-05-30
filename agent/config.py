"""Wira configuration — all knobs read from environment (.env)."""

import os
from pathlib import Path

AGENT_DIR = Path(__file__).parent

# --- Identity ---
OWNER_NAME = os.getenv("OWNER_NAME", "Craig")
ASSISTANT_NAME = os.getenv("ASSISTANT_NAME", "Wira")

# --- Brain (LLM provider) ---
# "chatgpt"   = Uses your ChatGPT subscription (default, no API key needed)
# "anthropic" = Claude API (needs ANTHROPIC_API_KEY)
# "openai"    = GPT API (needs OPENAI_API_KEY)
# "ollama"    = local model (private, free, needs Ollama running)
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "chatgpt").lower()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

# Default model per provider (overridable with LLM_MODEL)
_DEFAULT_MODEL = {
    "chatgpt": "gpt-4o",
    "anthropic": "claude-sonnet-4-6",
    "openai": "gpt-4o-mini",
    "ollama": "llama3.2:3b",
}
LLM_MODEL = os.getenv("LLM_MODEL") or _DEFAULT_MODEL.get(LLM_PROVIDER, "gpt-4o")

MAX_TOKENS = int(os.getenv("MAX_TOKENS", "400"))

# --- Behaviour ---
# Reply inside group chats too? Default: DMs only (groups get noisy fast).
REPLY_TO_GROUPS = os.getenv("REPLY_TO_GROUPS", "false").lower() in ("1", "true", "yes")

# Optional allowlist of phone numbers (digits only, no +). Empty = reply to everyone.
_raw_allow = os.getenv("ALLOWLIST", "").strip()
ALLOWLIST = {n.strip().lstrip("+") for n in _raw_allow.split(",") if n.strip()}

# --- Approval mode ---
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
SESSION_DB_PATH = os.getenv("SESSION_DB_PATH", str(AGENT_DIR / "session.sqlite3"))
# Conversation memory.
MEMORY_DB_PATH = os.getenv("MEMORY_DB_PATH", str(Path.home() / ".wira" / "memory.db"))

MAX_HISTORY_MESSAGES = int(os.getenv("MAX_HISTORY_MESSAGES", "20"))  # per-contact context
MAX_STORED_MESSAGES = int(os.getenv("MAX_STORED_MESSAGES", "5000"))  # global prune ceiling
