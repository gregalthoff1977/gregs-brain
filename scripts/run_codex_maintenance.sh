#!/usr/bin/env bash
set -euo pipefail

mkdir -p /data/.codex

export CODEX_HOME=/data/.codex
export WORKSPACE_PATH="${WORKSPACE_PATH:-/data/gregs-brain-workspace}"

cd /app

codex exec \
  --skip-git-repo-check \
  --sandbox danger-full-access \
  < /app/scripts/codex-maintenance-prompt.md