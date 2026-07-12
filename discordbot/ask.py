"""Answer questions against the wiki via an Anthropic tool loop.

Gives Claude three tools backed by the same handlers the MCP server exposes:
search_wiki, read_page, list_pages. Loops until Claude produces a final
text answer or MAX_TOOL_TURNS is hit.
"""

from __future__ import annotations

import anthropic

import settings
from vault import Vault

SYSTEM_PROMPT = (
    "You are the retrieval interface to Greg's personal wiki (an LLM Wiki "
    "knowledge base). Answer questions using ONLY what you find via the "
    "provided tools. Search first; read full pages when snippets aren't "
    "enough. Cite the wiki paths you drew from at the end of your answer. "
    "If the wiki doesn't contain the answer, say so plainly. Keep answers "
    "concise — this is a Discord chat, not a report. Hard limit: 1800 "
    "characters."
)

TOOLS = [
    {
        "name": "search_wiki",
        "description": "Full-text search across the wiki and its sources. Returns matching chunks with document paths.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "limit": {"type": "integer", "description": "Max results (default 8)"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "read_page",
        "description": "Read a full document by its path (as returned by search_wiki or list_pages).",
        "input_schema": {
            "type": "object",
            "properties": {"path": {"type": "string", "description": "Document path, e.g. /wiki/design/equate.md"}},
            "required": ["path"],
        },
    },
    {
        "name": "list_pages",
        "description": "List documents. Pass a directory path or glob to narrow (empty for top level).",
        "input_schema": {
            "type": "object",
            "properties": {"target": {"type": "string", "description": "Directory path or glob, empty for root"}},
            "required": [],
        },
    },
]

_client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)


async def answer(question: str, vault: Vault) -> str:
    messages: list[dict] = [{"role": "user", "content": question}]

    for _ in range(settings.MAX_TOOL_TURNS):
        response = await _client.messages.create(
            model=settings.ANTHROPIC_MODEL,
            max_tokens=1500,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

        if response.stop_reason != "tool_use":
            return _text_of(response) or "I couldn't produce an answer."

        messages.append({"role": "assistant", "content": response.content})
        results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            try:
                output = await _run_tool(vault, block.name, block.input)
            except Exception as e:  # surface tool errors to the model, don't crash
                output = f"Tool error: {e}"
            results.append(
                {"type": "tool_result", "tool_use_id": block.id, "content": output[:50_000]}
            )
        messages.append({"role": "user", "content": results})

    return "I hit my tool-use limit before finding a confident answer. Try narrowing the question."


async def _run_tool(vault: Vault, name: str, args: dict) -> str:
    if name == "search_wiki":
        return await vault.search(args["query"], limit=int(args.get("limit", 8)))
    if name == "read_page":
        return await vault.read(args["path"])
    if name == "list_pages":
        return await vault.list_documents(args.get("target", ""))
    return f"Unknown tool: {name}"


def _text_of(response) -> str:
    return "\n".join(b.text for b in response.content if b.type == "text").strip()
