#!/bin/bash
set -e

echo "============================================"
echo "  Wira for WhatsApp — Installer"
echo "============================================"
echo ""

AGENT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$AGENT_DIR"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'
ok()   { echo -e "${GREEN}[OK]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }

# --- Python venv ---
echo "--- Step 1: Python environment ---"
if ! command -v python3 &>/dev/null; then
    echo "python3 is required but not found. Install Python 3.10+ and re-run."
    exit 1
fi
python3 -m venv .venv
.venv/bin/pip install --upgrade pip -q
.venv/bin/pip install -q -r requirements.txt
ok "Dependencies installed into .venv"
echo ""

# --- .env ---
echo "--- Step 2: Configuration ---"
if [ -f .env ]; then
    ok ".env already exists (left untouched)"
else
    cp .env.example .env
    ok "Created .env from template"
    warn "Edit .env and set your ANTHROPIC_API_KEY (or switch LLM_PROVIDER=ollama)."
fi
echo ""

echo "============================================"
ok "Install complete."
echo ""
echo "Next:"
echo "  1. Edit .env  (set ANTHROPIC_API_KEY, OWNER_NAME)"
echo "  2. Start Wira:  .venv/bin/python main.py"
echo "  3. Scan the QR code with WhatsApp > Linked Devices"
echo "============================================"
