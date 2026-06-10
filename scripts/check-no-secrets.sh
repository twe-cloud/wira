#!/usr/bin/env bash
#
# Fail if a real secret (not a placeholder) appears in tracked source or in
# built artifacts (site/dist, agent/dist). Length-bounded patterns so test
# stubs like "sk_test_x" and ".env.example" placeholders don't trip it.
#
# Run locally:   bash scripts/check-no-secrets.sh
# In CI:         after `npm run build` so dist/ artifacts are scanned too.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PATTERN='sk_live_[A-Za-z0-9]{20,}|sk_test_[A-Za-z0-9]{24,}|rk_live_[A-Za-z0-9]{20,}|whsec_[A-Za-z0-9]{24,}|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{30,}|xox[baprs]-[A-Za-z0-9-]{12,}|-----BEGIN [A-Z ]*PRIVATE KEY-----'

# Working tree minus deps/VCS/binaries; dist/ is intentionally INCLUDED so we
# also scan compiled bundles.
hits="$(grep -rInE "$PATTERN" . \
  --exclude-dir=node_modules \
  --exclude-dir=.git \
  --exclude-dir=.venv \
  --exclude-dir=__pycache__ \
  --exclude-dir=.remember \
  --exclude-dir=.claude \
  --exclude-dir=.wrangler \
  --exclude='*.png' --exclude='*.ico' --exclude='*.icns' \
  --exclude='*.jpg' --exclude='*.jpeg' --exclude='*.gif' \
  --exclude='*.woff' --exclude='*.woff2' --exclude='*.ttf' \
  --exclude='package-lock.json' \
  --exclude='*.example' \
  --exclude='check-no-secrets.sh' \
  2>/dev/null | grep -vE 'REPLACE_ME' || true)"

if [ -n "$hits" ]; then
  echo "❌ Potential live secret(s) detected:"
  echo "$hits"
  exit 1
fi

echo "✅ No live secrets detected in source or build artifacts."
