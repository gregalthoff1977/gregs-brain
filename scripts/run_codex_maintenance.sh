#!/usr/bin/env bash
set -euo pipefail

export CODEX_HOME="${CODEX_HOME:-/app/.codex}"
export WORKSPACE_PATH="${WORKSPACE_PATH:-/app/wiki}"

mkdir -p "$CODEX_HOME"

cd /app

cat /app/scripts/codex-maintenance-prompt.md | \
codex exec \
  --skip-git-repo-check \
  --sandbox danger-full-access