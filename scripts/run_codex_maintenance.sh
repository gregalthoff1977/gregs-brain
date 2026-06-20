#!/usr/bin/env bash
set -euo pipefail

export CODEX_HOME=/app/.codex
export WORKSPACE_PATH=/data/gregs-brain-workspace

mkdir -p "$CODEX_HOME"
mkdir -p "$WORKSPACE_PATH/wiki"

echo "=== CODEX WORKER DEBUG ==="
date
pwd
echo "WORKSPACE_PATH=$WORKSPACE_PATH"
echo "--- prompt contains ---"
grep -n "ALL unprocessed" /app/scripts/codex-maintenance-prompt.md || true
echo "--- wiki before ---"
ls -lt "$WORKSPACE_PATH/wiki" | head
echo "Inbox count:"
find "$WORKSPACE_PATH/wiki/inbox" -type f | wc -l

cd "$WORKSPACE_PATH"

cat /app/scripts/codex-maintenance-prompt.md | \
timeout 900 \
codex exec \
  --skip-git-repo-check \
  --sandbox danger-full-access

echo "--- wiki after ---"
ls -lt "$WORKSPACE_PATH/wiki" | head
echo "Processed count:"
grep -R "Processed inbox item" "$WORKSPACE_PATH/wiki/log.md" | wc -l

echo "Maintenance completed"