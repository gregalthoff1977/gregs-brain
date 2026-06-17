"""Email webhook parsing helpers for local ingestion."""

from __future__ import annotations

import re
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from html import unescape

import yaml
from bs4 import BeautifulSoup


_SLUG_RE = re.compile(r"[^a-z0-9]+")


def parse_received_date(received_at: str) -> str:
    raw = received_at.strip()
    if raw.endswith("Z"):
        raw = f"{raw[:-1]}+00:00"
    try:
        parsed = datetime.fromisoformat(raw)
    except ValueError:
        try:
            parsed = parsedate_to_datetime(raw)
        except (TypeError, ValueError):
            parsed = datetime.now(UTC)
    if parsed.tzinfo:
        parsed = parsed.astimezone(UTC)
    return parsed.date().isoformat()


def slugify_subject(subject: str) -> str:
    slug = _SLUG_RE.sub("-", subject.strip().lower()).strip("-")
    return slug[:80].strip("-") or "untitled-email"


def html_to_markdown(html: str) -> str:
    soup = BeautifulSoup(html or "", "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    for tag in soup.find_all(["br", "p", "div", "li", "tr", "h1", "h2", "h3"]):
        tag.append("\n")

    for link in soup.find_all("a"):
        text = link.get_text(" ", strip=True)
        href = link.get("href")
        if text and href:
            link.replace_with(f"[{text}]({href})")

    text = soup.get_text("\n")
    text = unescape(text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def email_body_to_markdown(body_text: str | None, body_html: str | None) -> str:
    if body_text and body_text.strip():
        return body_text.strip()
    return html_to_markdown(body_html or "")


def build_email_markdown(
    *,
    sender: str,
    subject: str,
    body_html: str | None,
    body_text: str | None,
    received_at: str,
) -> str:
    body = email_body_to_markdown(body_text, body_html)
    metadata = {
        "title": subject.strip() or "Untitled email",
        "tags": ["email", "inbox"],
        "source": "email",
        "email": {
            "sender": sender,
            "subject": subject,
            "received_at": received_at,
            "has_body_html": bool(body_html and body_html.strip()),
            "has_body_text": bool(body_text and body_text.strip()),
        },
    }
    frontmatter = yaml.safe_dump(metadata, sort_keys=False, allow_unicode=False).strip()
    return f"---\n{frontmatter}\n---\n\n# {metadata['title']}\n\n{body}\n"
