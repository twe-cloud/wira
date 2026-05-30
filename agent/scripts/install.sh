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

PY_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PY_MAJOR=$(echo "$PY_VERSION" | cut -d. -f1)
PY_MINOR=$(echo "$PY_VERSION" | cut -d. -f2)

if [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 10 ]; }; then
    echo "Python 3.10+ is required (found $PY_VERSION). Please upgrade and re-run."
    exit 1
fi
ok "Python $PY_VERSION found"

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
fi
echo ""

# --- systemd (Linux only) ---
if [ "$(uname)" = "Linux" ] && command -v systemctl &>/dev/null; then
    echo "--- Step 3: Systemd service ---"
    SERVICE_FILE="$AGENT_DIR/scripts/wira.service"
    INSTALLED="/etc/systemd/system/wira.service"
    CURRENT_USER="$(whoami)"

    if [ -f "$SERVICE_FILE" ]; then
        sed -e "s|__USER__|$CURRENT_USER|g" -e "s|__AGENT_DIR__|$AGENT_DIR|g" \
            "$SERVICE_FILE" > /tmp/wira.service

        if [ "$(id -u)" -eq 0 ]; then
            cp /tmp/wira.service "$INSTALLED"
            systemctl daemon-reload
            ok "Systemd service installed (run: systemctl enable --now wira)"
        else
            warn "Run as root to install systemd service, or copy manually:"
            echo "  sudo cp /tmp/wira.service $INSTALLED && sudo systemctl daemon-reload"
        fi
        rm -f /tmp/wira.service
    fi
    echo ""
fi

echo "============================================"
ok "Install complete."
echo ""
echo "Next:"
echo "  1. Run the setup wizard:  .venv/bin/python setup.py"
echo "     (Choose your brain, set your name, scan the QR code)"
echo ""
echo "  OR configure manually:"
echo "     Edit .env (set LLM_PROVIDER, OWNER_NAME, etc.)"
echo "     Start Wira:  .venv/bin/python main.py"
echo "     Scan the QR code with WhatsApp > Linked Devices"
echo "============================================"
