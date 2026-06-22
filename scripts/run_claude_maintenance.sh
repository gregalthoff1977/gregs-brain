#!/usr/bin/env bash
set -e

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
Use the gregs-brain MCP server.

Read the workspace guide.

Find everything added to /data/gregs-brain-workspace since the last maintenance run.

Process new inbox items into the wiki:
- update existing pages where possible
- create new pages only where warranted
- maintain cross-references and citations
- append short processing notes to wiki/log.md
- do not delete raw inbox files
- do not write to /app/wiki
- do not create /app/wiki/wiki
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