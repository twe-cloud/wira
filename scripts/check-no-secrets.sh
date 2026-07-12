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

# Scan versioned source plus generated release output. Ignored local credential
# files (for example site/.dev.vars) are intentionally outside this boundary:
# they are runtime inputs, not source. Never print the matching line because a
# failed safety check must not leak the credential into CI or agent logs.
hits=()
while IFS= read -r -d '' file; do
  [ -f "$file" ] || continue
  case "$file" in
    scripts/check-no-secrets.sh|*.example|package-lock.json) continue ;;
  esac
  if grep -Iq . "$file" 2>/dev/null && grep -qE "$PATTERN" "$file" 2>/dev/null; then
    hits+=("$file")
  fi
done < <(
  if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    git ls-files -z
  else
    # nb-run deliberately omits .git. In that disposable mirror, scan the
    # source tree directly while excluding local runtime credentials and bulky
    # generated/dependency directories.
    find . -type f \
      ! -path './site/dist/*' ! -path './agent/dist/*' \
      ! -path '*/node_modules/*' ! -path '*/.venv/*' \
      ! -path '*/__pycache__/*' ! -path '*/.remember/*' \
      ! -path '*/.wrangler/*' ! -name '.env' ! -name '.env.*' \
      ! -name '.dev.vars' ! -name '.dev.vars.*' ! -name '*.pem' \
      ! -name '*.key' ! -name '*.p12' ! -name '*.pfx' ! -name '*.jks' \
      -print0
  fi
  [ ! -d site/dist ] || find site/dist -type f -print0
  [ ! -d agent/dist ] || find agent/dist -type f -print0
)

if [ "${#hits[@]}" -gt 0 ]; then
  echo "❌ Potential live secret(s) detected:"
  printf '  %s\n' "${hits[@]}"
  exit 1
fi

echo "✅ No live secrets detected in source or build artifacts."
