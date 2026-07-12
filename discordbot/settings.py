"""Discord bot settings.

Named `settings.py` (not `config.py`) deliberately: the mcp/ package is on
PYTHONPATH and owns the `config` module name. Reads env directly.
"""

import os


def _require(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required env var: {name}")
    return value


DISCORD_BOT_TOKEN = _require("DISCORD_BOT_TOKEN")
ANTHROPIC_API_KEY = _require("ANTHROPIC_API_KEY")

# Your Supabase user id (auth.users.id). All vault reads/writes are scoped
# to this user via the same RLS path the MCP server uses.
BRAIN_USER_ID = _require("BRAIN_USER_ID")

# Slug of the knowledge base to write into / search (e.g. "gregs-brain").
KB_SLUG = _require("KB_SLUG")

# Channel routing. Channel = verb: inbox captures, ask retrieves.
INBOX_CHANNEL_ID = int(_require("INBOX_CHANNEL_ID"))
ASK_CHANNEL_ID = int(_require("ASK_CHANNEL_ID"))
# Optional: bot-only digest/notification channel (0 disables).
DIGEST_CHANNEL_ID = int(os.getenv("DIGEST_CHANNEL_ID", "0"))

ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")
MAX_TOOL_TURNS = int(os.getenv("MAX_TOOL_TURNS", "8"))
