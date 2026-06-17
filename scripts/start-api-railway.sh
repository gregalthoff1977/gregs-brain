#!/usr/bin/env bash
set -euo pipefail

export WORKSPACE_PATH="${WORKSPACE_PATH:-/data/gregs-brain-workspace}"
export PORT="${PORT:-8000}"

mkdir -p "$WORKSPACE_PATH"

echo "Starting Gregs Brain API"
echo "WORKSPACE_PATH=$WORKSPACE_PATH"
echo "PORT=$PORT"

if [ ! -d "$WORKSPACE_PATH/.llmwiki" ]; then
  echo "Initializing Gregs Brain workspace at $WORKSPACE_PATH"
  python llmwiki init "$WORKSPACE_PATH" || ./llmwiki init "$WORKSPACE_PATH"
fi

exec python -m uvicorn api.main:app --host 0.0.0.0 --port "$PORT"