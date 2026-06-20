from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse

from config import settings

router = APIRouter()


@router.get("/api/wiki/{file_path:path}", response_class=PlainTextResponse)
def read_wiki(file_path: str):
    root = Path(settings.WORKSPACE_PATH).resolve() / "wiki"
    target = (root / file_path).resolve()

    if not str(target).startswith(str(root)):
        raise HTTPException(status_code=400, detail="Invalid path")

    if not target.exists() or not target.is_file():
        raise HTTPException(status_code=404, detail=f"Wiki file not found: {file_path}")

    if target.suffix != ".md":
        raise HTTPException(status_code=400, detail="Only markdown files are supported")

    return target.read_text(encoding="utf-8")
