#!/usr/bin/env bash
set -euo pipefail

mkdir -p /data/.codex

export CODEX_HOME=/data/.codex
export WORKSPACE_PATH="${WORKSPACE_PATH:-/data/gregs-brain-workspace}"

cd /app

codex exec < /app/scripts/codex-maintenance-prompt.md