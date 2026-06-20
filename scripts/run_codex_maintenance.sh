#!/usr/bin/env bash
set -euo pipefail

export CODEX_HOME=/app/.codex
export WORKSPACE_PATH=/data/gregs-brain-workspace

mkdir -p "$CODEX_HOME"
mkdir -p "$WORKSPACE_PATH/wiki"

cd /app

cat scripts/codex-maintenance-prompt.md | \
timeout 900 \
codex exec \
  --skip-git-repo-check \
  --sandbox danger-full-access

python scripts/refresh_wiki_overview.py
python scripts/check-wiki-maintenance.py

echo "Maintenance completed"
