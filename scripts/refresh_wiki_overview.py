from pathlib import Path
from datetime import datetime, timezone
import os

workspace = Path(os.environ.get("WORKSPACE_PATH", ".")).resolve()
wiki = workspace / "wiki"
inbox = wiki / "inbox"
overview = wiki / "overview.md"
log = wiki / "log.md"

inbox_files = sorted(inbox.glob("*.md")) if inbox.exists() else []
wiki_files = sorted(wiki.rglob("*.md"))
today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

overview.write_text(f"""---
title: Overview
description: Hub page for the Gregs Brain workspace wiki and its current source-derived findings.
date: {today}
tags:
- overview
- workspace
---

This wiki tracks source-derived notes and operational knowledge for `gregs-brain-workspace`.

## Scope

- Source count: {len(inbox_files)} inbox items stored in `/wiki/inbox/`.
- Wiki page count: {len(wiki_files)} markdown pages.

## Current State

The email-to-wiki ingest path is working. New material is being written into `/wiki/inbox/`, indexed into `.llmwiki/index.db`, and surfaced through `/api/brain/search`.

## Key Findings

- Current inbox material includes career strategy, systems thinking, AI workflows, creative leadership, personal operating models, and health notes.
- Most current material is still raw inbox content, not durable synthesized wiki pages.
- The next missing capability is an inbox synthesis pass that promotes raw notes into durable pages outside `/wiki/inbox/`.

## Recent Updates

- {today}: Refreshed overview from current inbox and wiki file state.

## Priority Next Step

Build durable synthesis pages from raw inbox material.
""", encoding="utf-8")

with log.open("a", encoding="utf-8") as f:
    f.write(f"""

## [{today}] maintenance | Automated overview refresh
- Refreshed overview.md from current filesystem state.
- Inbox item count: {len(inbox_files)}.
- Wiki markdown page count: {len(wiki_files)}.
- Key takeaway: ingest and search work; durable synthesis is still the next layer.
""")
