#!/usr/bin/env bash
set -euo pipefail

export CODEX_HOME="${CODEX_HOME:-/tmp/.codex}"
export WORKSPACE_PATH="${WORKSPACE_PATH:-/data/gregs-brain-workspace}"
export CODEX_API_KEY="${CODEX_API_KEY:-${OPENAI_API_KEY:-}}"

mkdir -p "$CODEX_HOME"

cd /app

cat /app/scripts/codex-maintenance-prompt.md | \
codex exec \
  --skip-git-repo-check \
  --sandbox danger-full-access