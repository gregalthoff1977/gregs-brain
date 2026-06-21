# Claude Code MCP Setup

Gregs Brain maintenance now runs through Claude Code connected to the local LLM Wiki MCP server. Railway remains the capture/API layer; it should not run a wiki maintenance worker.

## MCP Command

Use the original CLI entry against the persistent Railway volume workspace:

```bash
./llmwiki mcp /data/gregs-brain-workspace
```

Claude Code should run maintenance against:

```text
/data/gregs-brain-workspace
```

Do not point maintenance at:

```text
/app/wiki
/app/wiki/wiki
repo-local wiki folders
```

## Claude Code Config

Generate a config snippet:

```bash
./llmwiki mcp-config /data/gregs-brain-workspace
```

Add the resulting server entry to Claude Code's MCP settings. The command must resolve to this repository's `llmwiki` executable and pass `mcp /data/gregs-brain-workspace`.

## Maintenance Prompt

Use this prompt for Claude Code maintenance runs:

```text
Read the guide. Find everything added to the workspace since your last run - new sources, clips, and highlights. For each one, read it and update the wiki: write new pages where warranted, fold new material into existing pages, and fix any cross-references or citations it affects. Append a short note to wiki/log.md summarizing what changed.
```

## Validation

Run on Railway or any shell with the `/data/gregs-brain-workspace` volume mounted:

```bash
cd /data/gregs-brain-workspace/wiki
grep -R "Processed inbox item" log.md | wc -l
```

Expected:

- Count is greater than 2.
- `overview.md` reflects the latest processed date.
- `log.md` lists processed inbox items.
- There is no nested shadow wiki.

Check for a shadow wiki:

```bash
find /data/gregs-brain-workspace/wiki -type d -name wiki -print
```

Expected: no output.
