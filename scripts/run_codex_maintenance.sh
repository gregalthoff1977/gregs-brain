#!/usr/bin/env bash
set -euo pipefail

WORKSPACE_PATH="${WORKSPACE_PATH:-/data/gregs-brain-workspace}"
CODEX_HOME="${CODEX_HOME:-/data/.codex}"

export CODEX_HOME

cd /app

codex exec --config /app/.codex/config.toml < /app/scripts/codex-maintenance-prompt.md
