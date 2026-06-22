#!/usr/bin/env bash
set -euo pipefail

useradd -m claudeuser 2>/dev/null || true

mkdir -p /app/.claude

cat >/app/.claude/mcp.json <<EOF
{
  "mcpServers": {
    "gregs-brain": {
      "command": "/app/llmwiki",
      "args": ["mcp", "/data/gregs-brain-workspace"]
    }
  }
}
EOF

cat >/tmp/maintenance-prompt.txt <<EOF
Use only the gregs-brain MCP server.

Do not inspect repository files.
Do not read source code.
Do not run shell commands.
Do not inspect /app, /app/wiki, mcp, api, scripts, tests, or Docker files.

Goal:
Process only new inbox items since the last maintenance entry in wiki/log.md.

Steps:
1. Call guide.
2. Identify the knowledge base.
3. Read wiki/log.md only to find the last maintenance boundary.
4. Search/list inbox sources only.
5. If no new inbox items exist, append one short log.md entry and stop.
6. If new inbox items exist, read only those new inbox items and directly relevant wiki pages.
7. Update existing pages where possible.
8. Create new pages only when clearly warranted.
9. Append concise processing notes to wiki/log.md.

Limits:
- Maximum 20 source reads.
- Maximum 10 wiki page reads.
- Maximum 10 edits.
- Do not run lint unless pages changed.
- Do not summarize unchanged wiki content.

Hard constraints:
- Do not delete raw inbox files.
- Do not write to /app/wiki.
- Do not create /app/wiki/wiki.

Report only:
- inbox items processed
- pages created
- pages updated
- log.md entries added
EOF

chown -R claudeuser:claudeuser \
  /app/.claude \
  /tmp/maintenance-prompt.txt \
  /data/gregs-brain-workspace

su - claudeuser -c "
cd /app &&
export ANTHROPIC_API_KEY='$ANTHROPIC_API_KEY' &&
claude \
  --dangerously-skip-permissions \
  --mcp-config /app/.claude/mcp.json \
  --print \
  < /tmp/maintenance-prompt.txt
"

chown -R root:root /data/gregs-brain-workspace