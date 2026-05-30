#!/bin/bash
# Build Wira.app — standalone Mac application
set -e

AGENT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$AGENT_DIR"

echo "Building Wira.app..."
echo ""

# Ensure venv and deps
if [ ! -d .venv ]; then
    python3 -m venv .venv
fi
.venv/bin/pip install --upgrade pip -q
.venv/bin/pip install -q -r requirements.txt

# Build with PyInstaller
.venv/bin/pyinstaller wira.spec --clean --noconfirm

# Output
APP="$AGENT_DIR/dist/Wira.app"
if [ -d "$APP" ]; then
    echo ""
    echo "Build complete: $APP"
    echo ""
    echo "To distribute:"
    echo "  1. Create a DMG:  hdiutil create -volname Wira -srcfolder dist/Wira.app -ov dist/Wira.dmg"
    echo "  2. Upload to GitHub releases or host on nibiashara.biz"
else
    echo "Build failed — check output above."
    exit 1
fi
