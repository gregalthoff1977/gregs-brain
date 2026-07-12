"""Greg's Brain — Discord interface.

Channel = verb:
  #brain-inbox  → every message is captured as a note in /wiki/inbox/
  #brain-ask    → every message is answered from the wiki (threaded reply)
  #brain-digest → bot-only output (optional; POST /notify from routines)

Runs a tiny aiohttp server alongside the gateway so other services in the
Railway project (API, nightly routines) can push digest messages.
"""

from __future__ import annotations

import asyncio
import logging

import discord
from aiohttp import web

import settings
from ask import answer
from vault import Vault

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("brainbot")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
vault = Vault()


@client.event
async def on_ready():
    log.info("Logged in as %s", client.user)


@client.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    if message.channel.id == settings.INBOX_CHANNEL_ID:
        await _handle_inbox(message)
    elif message.channel.id == settings.ASK_CHANNEL_ID:
        await _handle_ask(message)


async def _handle_inbox(message: discord.Message):
    try:
        result = await vault.capture_note(
            author=message.author.display_name,
            content=message.content or "",
            attachments=[a.url for a in message.attachments],
        )
        await message.add_reaction("✅")
        log.info("Captured note: %s", result.splitlines()[0] if result else "")
    except Exception:
        log.exception("Inbox capture failed")
        await message.add_reaction("❌")
        await message.reply("Couldn't save that — check the logs.", mention_author=False)


async def _handle_ask(message: discord.Message):
    question = message.content.strip()
    if not question:
        return
    async with message.channel.typing():
        try:
            reply = await answer(question, vault)
        except Exception:
            log.exception("Ask failed")
            reply = "Something broke while searching the wiki — check the logs."
    # Thread the reply so follow-ups stay grouped
    for chunk in _split(reply, 1900):
        await message.reply(chunk, mention_author=False)


def _split(text: str, size: int) -> list[str]:
    return [text[i : i + size] for i in range(0, len(text), size)] or ["(empty)"]


# ── /notify endpoint for digests ─────────────────────────────────────

async def _notify(request: web.Request) -> web.Response:
    if not settings.DIGEST_CHANNEL_ID:
        return web.json_response({"error": "digest channel not configured"}, status=400)
    body = await request.json()
    text = str(body.get("message", "")).strip()
    if not text:
        return web.json_response({"error": "message required"}, status=400)
    channel = client.get_channel(settings.DIGEST_CHANNEL_ID)
    if channel is None:
        return web.json_response({"error": "channel not found"}, status=404)
    for chunk in _split(text, 1900):
        await channel.send(chunk)
    return web.json_response({"ok": True})


async def _health(_request: web.Request) -> web.Response:
    return web.json_response({"ok": client.is_ready()})


async def _run_http():
    app = web.Application()
    app.router.add_post("/notify", _notify)
    app.router.add_get("/health", _health)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()
    log.info("HTTP listening on :8080")


async def main():
    async with client:
        asyncio.create_task(_run_http())
        await client.start(settings.DISCORD_BOT_TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
