Read the LLM wiki guide first.

Then process ALL unprocessed files in /data/gregs-brain-workspace/wiki/inbox.

Rules:
- The ONLY wiki root is /data/gregs-brain-workspace/wiki.

Never prepend "wiki/" to paths.
Always write directly into:
- overview.md
- log.md
- inbox-insights.md
- inbox/*
relative to that root.

Before making changes, run:
pwd
ls -la
find . -maxdepth 2 -type f

Abort if any proposed path contains /wiki/wiki/.

- Preserve every raw inbox file.
- Do not create one page per inbox item.
- Group related inbox items into durable synthesis pages.
- Update existing pages before creating new ones.
- Create new concept/entity/index pages only when warranted.
- Maintain citations and cross-links.
- Update /data/gregs-brain-workspace/wiki/overview.md.
- Append a log entry to /data/gregs-brain-workspace/wiki/log.md listing every inbox item processed.
- Run available lint/checks.
- Do not stop after one inbox file.
- If there are many inbox files, process them in batches but continue until the inbox backlog is addressed.
- Do not invent a new structure.
- After all writes, print a summary listing every modified file with absolute paths.