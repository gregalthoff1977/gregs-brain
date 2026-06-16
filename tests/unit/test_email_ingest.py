from services.email_ingest import (
    build_email_markdown,
    email_body_to_markdown,
    parse_received_date,
    slugify_subject,
)


def test_slugify_subject():
    assert slugify_subject("Hello, Greg: AI Workflow Builder!") == "hello-greg-ai-workflow-builder"


def test_parse_received_date_from_iso_z():
    assert parse_received_date("2026-06-16T20:30:00Z") == "2026-06-16"


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
