#!/usr/bin/env bash
set -euo pipefail

export CODEX_HOME=/app/.codex
export WORKSPACE_PATH=/app/wiki

mkdir -p "$CODEX_HOME"

cd /app

cat scripts/codex-maintenance-prompt.md | \
timeout 900 \
codex exec \
  --skip-git-repo-check \
  --sandbox danger-full-access

echo "Maintenance completed"