from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from deps import get_document_service, get_kb_service
from services.base import DocumentService, KBService
from services.email_ingest import build_email_markdown, parse_received_date, slugify_subject

router = APIRouter(prefix="/ingest", tags=["ingest"])


class EmailIngestRequest(BaseModel):
    sender: str = Field(max_length=512)
    subject: str = Field(max_length=512)
    body_html: str | None = Field(default=None, max_length=10 * 1024 * 1024)
    body_text: str | None = Field(default=None, max_length=10 * 1024 * 1024)
    received_at: str = Field(max_length=128)


class PostmarkAddress(BaseModel):
    model_config = ConfigDict(extra="ignore")

    Email: str | None = Field(default=None, max_length=512)


class PostmarkInboundRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")

    FromFull: PostmarkAddress | None = None
    From: str | None = Field(default=None, max_length=512)
    Subject: str | None = Field(default=None, max_length=512)
    HtmlBody: str | None = Field(default=None, max_length=10 * 1024 * 1024)
    TextBody: str | None = Field(default=None, max_length=10 * 1024 * 1024)
    Date: str | None = Field(default=None, max_length=128)

    def to_email_ingest_request(self) -> EmailIngestRequest:
        sender = (self.FromFull.Email if self.FromFull else None) or self.From or ""
        return EmailIngestRequest(
            sender=sender,
            subject=self.Subject or "",
            body_html=self.HtmlBody,
            body_text=self.TextBody,
            received_at=self.Date or "",
        )


@router.post("/email", status_code=201)
async def ingest_email(
    body: EmailIngestRequest,
    kb_service: Annotated[KBService, Depends(get_kb_service)],
    document_service: Annotated[DocumentService, Depends(get_document_service)],
):
    return await _create_email_page(body, kb_service, document_service)


@router.post("/email/postmark", status_code=201)
async def ingest_postmark_email(
    body: PostmarkInboundRequest,
    kb_service: Annotated[KBService, Depends(get_kb_service)],
    document_service: Annotated[DocumentService, Depends(get_document_service)],
):
    return await _create_email_page(body.to_email_ingest_request(), kb_service, document_service)


async def _create_email_page(
    body: EmailIngestRequest,
    kb_service: KBService,
    document_service: DocumentService,
):
    kbs = await kb_service.list()
    if not kbs:
        raise HTTPException(status_code=500, detail="No local knowledge base initialized")

    kb_id = str(kbs[0]["id"])
    date_slug = parse_received_date(body.received_at)
    subject_slug = slugify_subject(body.subject)
    filename = await _next_available_filename(document_service, kb_id, date_slug, subject_slug)
    path = "/wiki/inbox/"
    content = build_email_markdown(
        sender=body.sender,
        subject=body.subject,
        body_html=body.body_html,
        body_text=body.body_text,
        received_at=body.received_at,
    )

    doc = await document_service.create_note(kb_id, filename, path, content)
    wiki_path = f"{path}{filename}"
    return {
        "wiki_path": wiki_path,
        "path": wiki_path,
        "document_id": str(doc["id"]),
    }


async def _next_available_filename(
    document_service: DocumentService,
    kb_id: str,
    date_slug: str,
    subject_slug: str,
) -> str:
    existing = await document_service.list(kb_id, path="/wiki/inbox/")
    filenames = {doc.get("filename") for doc in existing}
    base = f"{date_slug}-{subject_slug}"
    filename = f"{base}.md"
    if filename not in filenames:
        return filename
    for suffix in range(2, 1000):
        candidate = f"{base}-{suffix}.md"
        if candidate not in filenames:
            return candidate
    raise HTTPException(status_code=409, detail="Too many emails with the same subject and date")
