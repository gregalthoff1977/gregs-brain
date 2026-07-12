"""Vault access for the Discord bot.

Reuses the MCP tool layer directly (mcp/ is on PYTHONPATH), so writes and
searches behave identically to Claude working over MCP — same frontmatter
handling, same reference syncing, same RLS scoping.
"""

from __future__ import annotations

import re
from datetime import UTC, datetime

from tools.read import ReadHandler
from tools.search import SearchHandler
from tools.write import WriteHandler
from vaultfs.postgres import PostgresVaultFS

import settings

_SLUG_RE = re.compile(r"[^a-z0-9]+")

INBOX_PATH = "/wiki/inbox/"


class Vault:
    """One user-scoped handle to the knowledge base."""

    def __init__(self):
        self.fs = PostgresVaultFS(settings.BRAIN_USER_ID)
        self._kb: dict | None = None

    async def kb(self) -> dict:
        if self._kb is None:
            kb = await self.fs.resolve_kb(settings.KB_SLUG)
            if not kb:
                raise RuntimeError(f"Knowledge base '{settings.KB_SLUG}' not found for user")
            self._kb = kb
        return self._kb

    # ── Capture ──────────────────────────────────────────────────────

    async def capture_note(self, *, author: str, content: str, attachments: list[str]) -> str:
        """Save a Discord message as an inbox note. Returns the write result string."""
        kb = await self.kb()
        now = datetime.now(UTC)
        title = _derive_title(content, now)

        body_parts = [content.strip()] if content.strip() else []
        if attachments:
            links = "\n".join(f"- {url}" for url in attachments)
            body_parts.append(f"## Attachments\n\n{links}")
        body = "\n\n".join(body_parts) or "(no text)"

        note = (
            f"{body}\n\n"
            f"---\n"
            f"*Captured from Discord by {author} at {now.strftime('%Y-%m-%d %H:%M UTC')}.*\n"
        )

        handler = WriteHandler(self.fs, kb)
        return await handler.create(
            path=INBOX_PATH,
            title=title,
            content=note,
            tags=["discord", "inbox"],
            date_str=now.date().isoformat(),
            overwrite=False,
        )

    # ── Retrieval (used as tools by the Anthropic loop) ──────────────

    async def search(self, query: str, limit: int = 8) -> str:
        kb = await self.kb()
        handler = SearchHandler(self.fs, kb)
        return await handler.search_chunks(query=query, path="", tags=None, limit=limit)

    async def read(self, path: str) -> str:
        kb = await self.kb()
        handler = ReadHandler(self.fs, kb)
        result = await handler.read(path, pages="", sections=None, include_images=False)
        if isinstance(result, list):  # mixed content blocks — keep text only
            return "\n".join(
                block.text for block in result if getattr(block, "text", None)
            ) or "(non-text content)"
        return result

    async def list_documents(self, target: str = "") -> str:
        kb = await self.kb()
        handler = SearchHandler(self.fs, kb)
        return await handler.list_documents(target=target, tags=None)


def _derive_title(content: str, now: datetime) -> str:
    first_line = next((ln.strip() for ln in content.splitlines() if ln.strip()), "")
    first_line = re.sub(r"^#+\s*", "", first_line)
    if first_line:
        words = first_line.split()
        title = " ".join(words[:10])
        if len(words) > 10:
            title += "…"
        return title[:120]
    return f"Discord note {now.strftime('%Y-%m-%d %H:%M')}"
