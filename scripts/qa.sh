#!/usr/bin/env bash
# Wira production-readiness QA.
#
# Runs every check that a machine can settle on its own, prints a scoreboard,
# and exits non-zero if any of them fail. The checks that need a human or real
# hardware are listed at the end rather than silently skipped, because a suite
# that quietly drops them reads as "everything passed" when it did not.
#
#   ./scripts/qa.sh                      # code + live-surface checks
#   ./scripts/qa.sh --exe path/to/x.exe  # also verify a signed Windows installer
#   ./scripts/qa.sh --offline            # skip checks that need the network
#
set -uo pipefail

cd "$(dirname "$0")/.." || exit 1

EXE=""
OFFLINE=0
while [ $# -gt 0 ]; do
  case "$1" in
    --exe) EXE="${2:-}"; shift 2 ;;
    --offline) OFFLINE=1; shift ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

PASS=0; FAIL=0; SKIP=0
RESULTS=()

record() { # record <status> <name> [detail]
  case "$1" in
    PASS) PASS=$((PASS + 1)) ;;
    FAIL) FAIL=$((FAIL + 1)) ;;
    SKIP) SKIP=$((SKIP + 1)) ;;
  esac
  RESULTS+=("$1|$2|${3:-}")
  printf '  [%s] %s%s\n' "$1" "$2" "${3:+ — $3}"
}

run() { # run <name> <command...>
  local name="$1"; shift
  if out=$("$@" 2>&1); then
    record PASS "$name"
  else
    record FAIL "$name" "$(printf '%s' "$out" | tail -n 3 | tr '\n' ' ')"
  fi
}

echo "== agent =="
# The GUI tests construct Tk widgets. On a headless box that blocks forever, so
# CI wraps this in xvfb-run; do the same here when a display is unavailable.
AGENT_PY="${WIRA_QA_PYTHON:-python3}"
if [ "$(uname)" != "Darwin" ] && [ -z "${DISPLAY:-}" ] && command -v xvfb-run >/dev/null 2>&1; then
  run "agent unit suite (76 tests)" env -C agent xvfb-run -a "$AGENT_PY" -m unittest
else
  run "agent unit suite (76 tests)" env -C agent "$AGENT_PY" -m unittest
fi

echo "== site + worker =="
run "site typecheck"              env -C site npx --no-install tsc --noEmit
run "worker unit suite (vitest)"  env -C site npx --no-install vitest run
run "site production build"       env -C site npm run build
run "worker deploy dry-run"       env -C site npx --no-install wrangler deploy --dry-run

echo "== supply chain / secrets =="
run "no live secrets in source or build output" bash scripts/check-no-secrets.sh

echo "== code signing =="
if [ -n "$EXE" ]; then
  run "windows installer is signed by Ni Biashara + timestamped" \
    python3 scripts/verify-authenticode.py "$EXE"
else
  record SKIP "windows installer signature" "no --exe given"
fi

if [ "$(uname)" = "Darwin" ]; then
  DMG="${WIRA_QA_DMG:-}"
  if [ -n "$DMG" ] && [ -f "$DMG" ]; then
    if spctl -a -t open --context context:primary-signature "$DMG" >/dev/null 2>&1; then
      record PASS "mac dmg is notarized + Gatekeeper-accepted"
    else
      record FAIL "mac dmg is notarized + Gatekeeper-accepted"
    fi
  else
    record SKIP "mac dmg notarization" "set WIRA_QA_DMG=path/to/Wira.dmg"
  fi
else
  record SKIP "mac dmg notarization" "needs macOS (spctl)"
fi

echo "== live surfaces =="
if [ "$OFFLINE" = "1" ]; then
  record SKIP "live site routes" "--offline"
else
  probe() { # probe <name> <url> <expected-status>
    local got
    got=$(curl -sS -o /dev/null -w '%{http_code}' -X HEAD --max-time 20 "$2" 2>/dev/null)
    if [ "$got" = "$3" ]; then
      record PASS "$1" "HTTP $got"
    else
      record FAIL "$1" "expected HTTP $3, got ${got:-none}"
    fi
  }
  BASE="${WIRA_QA_BASE:-https://wira.nibiashara.biz}"
  probe "site root serves"                  "$BASE/"                 200
  probe "mac download redirects to release" "$BASE/download/mac"     302
  # 202 = the deliberate coming-soon hold. Flip this to 302 in the same commit
  # that makes the Windows download public, so the suite guards the new state.
  probe "windows download still gated"      "$BASE/download/windows" 202
fi

echo
echo "======================================"
printf 'passed %d   failed %d   skipped %d\n' "$PASS" "$FAIL" "$SKIP"
echo "======================================"

cat <<'HUMAN'

Not covered here — these need a human on real hardware, and the public Windows
download must stay gated until they pass (docs/qa/windows-smoke-checklist.md):

  - Windows: GUI renders at 125%/150% scaling; pick-a-brain flow completes.
  - Windows: QR pairing against a real phone; Wira replies to a WhatsApp message.
  - Windows: restart persistence (no re-pair, no re-key) + Startup shortcut.
  - Stripe: test-mode checkout -> /success -> webhook -> download email.
  - Fresh install defaults: owner-lock ON, confirmation ON, balanced preset.
HUMAN

[ "$FAIL" -eq 0 ] || exit 1
