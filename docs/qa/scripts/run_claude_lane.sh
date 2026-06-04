#!/usr/bin/env bash
set -euo pipefail
if [ "$#" -ne 4 ]; then
  echo "usage: $0 <prompt-file> <workdir> <log-file> <handoff-file>" >&2
  exit 2
fi
PROMPT_FILE="$1"
WORKDIR="$2"
LOG_FILE="$3"
HANDOFF_FILE="$4"
mkdir -p "$(dirname "$LOG_FILE")"
cd "$WORKDIR"
{
  echo "[lane-start] $(date -Iseconds)"
  echo "[workdir] $WORKDIR"
  echo "[prompt] $PROMPT_FILE"
  echo "[handoff] $HANDOFF_FILE"
} >> "$LOG_FILE"
set +e
claude -p "$(cat "$PROMPT_FILE")" --max-turns 30 --model sonnet --effort high >> "$LOG_FILE" 2>&1
STATUS=$?
set -e
{
  echo "[lane-exit] $(date -Iseconds) status=$STATUS"
  if [ -f "$HANDOFF_FILE" ]; then
    echo "[handoff-present] yes"
  else
    echo "[handoff-present] no"
  fi
} >> "$LOG_FILE"
exit "$STATUS"
