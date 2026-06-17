from services.email_ingest import (
    build_email_markdown,
    email_body_to_markdown,
    parse_received_date,
    slugify_subject,
)
from routes.ingest import PostmarkInboundRequest, ingest_postmark_email


def test_slugify_subject():
    assert slugify_subject("Hello, Greg: AI Workflow Builder!") == "hello-greg-ai-workflow-builder"


def test_parse_received_date_from_iso_z():
    assert parse_received_date("2026-06-16T20:30:00Z") == "2026-06-16"


def test_parse_received_date_from_email_header_date():
    assert parse_received_date("Tue, 16 Jun 2026 20:30:00 +0000") == "2026-06-16"


def test_html_body_converts_to_markdown_links():
    markdown = email_body_to_markdown(None, '<p>Read <a href="https://example.com">this</a></p>')

    assert "[this](https://example.com)" in markdown


def test_build_email_markdown_stores_metadata_and_tags():
    markdown = build_email_markdown(
        sender="sender@example.com",
        subject="Newsletter",
        body_html="<p>HTML body</p>",
        body_text=None,
        received_at="2026-06-16T20:30:00Z",
    )

    assert "tags:" in markdown
    assert "- email" in markdown
    assert "- inbox" in markdown
    assert "sender: sender@example.com" in markdown
    assert "received_at: '2026-06-16T20:30:00Z'" in markdown
    assert "# Newsletter" in markdown
    assert "HTML body" in markdown


class FakeKBService:
    async def list(self):
        return [{"id": "kb-1"}]


class FakeDocumentService:
    def __init__(self):
        self.created = None

    async def list(self, kb_id, path=None):
        return []

    async def create_note(self, kb_id, filename, path, content):
        self.created = {
            "kb_id": kb_id,
            "filename": filename,
            "path": path,
            "content": content,
        }
        return {"id": "doc-1"}


async def test_postmark_inbound_creates_inbox_email_page_with_tags():
    payload = {
        "FromName": "Newsletter Sender",
        "From": "Newsletter Sender <fallback@example.com>",
        "FromFull": {
            "Email": "sender@example.com",
            "Name": "Newsletter Sender",
            "MailboxHash": "",
        },
        "To": "\"Greg\" <inbox@example.com>",
        "ToFull": [{"Email": "inbox@example.com", "Name": "Greg", "MailboxHash": ""}],
        "Subject": "Postmark Weekly: AI links",
        "MessageID": "f483e4be-61f0-4c21-9c1f-0f75a2d8d837",
        "Date": "Tue, 16 Jun 2026 20:30:00 +0000",
        "TextBody": "Plain text fallback\n\nhttps://example.com",
        "HtmlBody": "<html><body><p>Read <a href=\"https://example.com\">this</a></p></body></html>",
        "Attachments": [],
    }
    document_service = FakeDocumentService()

    response = await ingest_postmark_email(
        PostmarkInboundRequest.model_validate(payload),
        FakeKBService(),
        document_service,
    )

    assert response["wiki_path"] == "/wiki/inbox/2026-06-16-postmark-weekly-ai-links.md"
    assert document_service.created["kb_id"] == "kb-1"
    assert document_service.created["path"] == "/wiki/inbox/"
    assert document_service.created["filename"] == "2026-06-16-postmark-weekly-ai-links.md"
    markdown = document_service.created["content"]
    assert "- email" in markdown
    assert "- inbox" in markdown
    assert "sender: sender@example.com" in markdown
    assert "subject: 'Postmark Weekly: AI links'" in markdown
    assert "received_at: Tue, 16 Jun 2026 20:30:00 +0000" in markdown
    assert "Plain text fallback" in markdown
